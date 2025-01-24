#region modules
from xctph.elph import Elph
from xctph.xct import Xct
from xctph.utils.k_plus_q import get_all_kq_maps
from mpi4py import MPI 
import h5py
from fp.inputs.input_main import Input 
from fp.io.pkl import load_obj 
import numpy as np 
#endregion

#region variables
#endregion

#region functions
#endregion

#region classes
class ParSize:
    def __init__(self, shape, comm: MPI.Comm):
        self.shape = shape
        self.array_size: int = int(np.prod(np.array(shape)))
        self.comm: MPI.Comm = comm

        # Do the setup here.
        self.mpi_size = comm.Get_size()
        self.mpi_rank = comm.Get_rank()
        self._calc_local_ranges()

    def _calc_local_ranges(self):
       self.local_size_avg = self.array_size // self.mpi_size
       self.local_size_max = self.local_size_avg + self.array_size -  (self.array_size // self.mpi_size ) * self.mpi_size
       self.local_size = self.local_size_avg if self.mpi_rank != self.mpi_size-1 else self.local_size_max
       self.local_start = self.local_size_avg * self.mpi_rank  
       self.local_end = self.local_start + self.local_size 

    def get_local_range(self):
        return (self.local_start, self.local_end)

    def get_idx(self, linear_idx):
        assert linear_idx < self.array_size, f'Linear idx: {linear_idx} is greater than array size: {self.array_size}'
        
        array_idx = list(None for _ in range(len(self.shape)))
        current_index = linear_idx
        for dim in range(len(self.shape)-1):
            stride = int(np.prod(self.shape[dim+1:]))
            array_idx[dim] = current_index // stride
            current_index = current_index % stride
        array_idx[-1] = current_index 

        return array_idx 

        return output 

class Xctph:
    def __init__(
        self, 
        input_filename: str = './input.pkl',
        add_electron_part: bool = True,
        add_hole_part: bool = True,
    ):
        self.input: Input = load_obj(input_filename)
        self.add_electron_part = add_electron_part
        self.add_hole_part = add_hole_part

    def generate_elph(self):
        elph = Elph()
        elph.read()
        elph.write()

    def read_elph(self):
        with h5py.File('./elph.h5', 'r') as f:
            self.nmodes = f['elph_header/nmode'][()]
            self.nk_elph = f['elph_header/nk'][()]
            self.kpts_elph = f['elph_header/kpts'][()]
            self.nq = f['elph_header/nq'][()]
            self.qpts = f['elph_header/qpts'][()]
            self.k_plus_q_map = f['elph_header/k_plus_q_map'][()]
            self.k_minus_q_map = f['elph_header/k_minus_q_map'][()]
            self.frequencies = f['elph_data/frequencies'][()]
            self.gkq = f['elph_data/elph_mode'][()]

    def generate_xct(self):
        xct = Xct()
        xct.read()
        xct.write()

    def read_xct(self):
        with h5py.File('./xct.h5', 'r') as f:
            self.nbnd = f['/exciton_header/nevecs'][()]
            self.nv = f['/exciton_header/nv'][()]
            self.nc = f['/exciton_header/nc'][()]
            self.nk = f['/exciton_header/nk'][()]
            self.kpts = f['/exciton_header/kpts'][()]
            self.nQ = f['/exciton_header/nQ'][()]
            self.Qpts = f['/exciton_header/center_of_mass_Q'][()]
            self.energies = f['/exciton_data/eigenvalues'][()]
            self.avck = f['/exciton_data/eigenvectors'][()]

    def read_input(self):
        self.nbnd_xct = int(self.input.input_dict['xctph']['num_evecs'])

    def calc(self):
        # Preliminaries.
        self.comm = MPI.COMM_WORLD
        # Only generate from the rank 0. 
        if self.comm.Get_rank()==0:
            self.generate_elph()
            self.generate_xct()
        self.read_elph()
        self.read_xct()
        self.read_input()

        # Checks.
        assert self.nk_elph == self.nk
        assert self.nbnd >= self.nbnd_xct

        # Calculate.
        # generate additional kq maps
        self.Q_plus_q_map = get_all_kq_maps(self.Qpts, self.qpts)
        k_minus_Q_map = get_all_kq_maps(self.kpts, self.Qpts, -1.0)

        # Parallel version.
        self.xctbnd_parsize = ParSize(shape=(self.nbnd_xct, self.nbnd_xct), comm=self.comm)
        self.xct_start, self.xct_end = self.xctbnd_parsize.get_local_range()
        self.gQq_eh: np.ndarray = np.zeros((self.xct_end - self.xct_start, self.nQ, self.nmodes, self.nq), 'c16')
        self.gQq_e: np.ndarray = np.zeros((self.xct_end - self.xct_start, self.nQ, self.nmodes, self.nq), 'c16')
        self.gQq_h: np.ndarray = np.zeros((self.xct_end - self.xct_start, self.nQ, self.nmodes, self.nq), 'c16')

        cb = slice(self.nv, self.nv + self.nc)
        vb = slice(0, self.nv)

        for iQ in range(self.nQ):
            for iq in range(self.nq):
                iQ_plus_q = self.Q_plus_q_map[iQ, iq]

                for ik in range(self.nk):
                    ik_plus_q = self.k_plus_q_map[ik, iq]
                    ik_minus_Q = k_minus_Q_map[ik, iQ]

                    for mnb in range(self.xct_start, self.xct_end):
                        mb, nb = self.xctbnd_parsize.get_idx(mnb)
                        # electron channel
                        aQ_e = self.avck[0, :, :, ik, nb, iQ]
                        aQq_e = self.avck[0, :, :, ik_plus_q, mb, iQ_plus_q]
                        gkq_e = self.gkq[cb, cb, ik, :, iq]

                        if self.add_electron_part:
                            self.gQq_eh[mnb - self.xct_start, iQ, :, iq] += np.einsum('vc,cdn,vd->n', aQq_e.conj(), gkq_e, aQ_e)
                            self.gQq_e[mnb - self.xct_start, iQ, :, iq] += np.einsum('vc,cdn,vd->n', aQq_e.conj(), gkq_e, aQ_e)

                        # hole channel
                        aQ_h = self.avck[0, :, :, ik_plus_q, nb, iQ]
                        aQq_h = self.avck[0, :, :, ik_plus_q, mb, iQ_plus_q]
                        gkq_h = self.gkq[vb, vb, ik_minus_Q, :, iq][::-1, ::-1, :]

                        if self.add_hole_part:
                            self.gQq_eh[mnb - self.xct_start, iQ, :, iq] -= np.einsum('vc,wvn,wc->n', aQq_h.conj(), gkq_h, aQ_h)
                            self.gQq_h[mnb - self.xct_start, iQ, :, iq] -= np.einsum('vc,wvn,wc->n', aQq_h.conj(), gkq_h, aQ_h)

                    if self.comm.Get_rank()==0:
                        print(f'Done Q: {iQ}, q: {iq}, k: {ik}', flush=True)
        
        print('Done loop', flush=True)
        
    def write(self):
        xctph_dict = {
            # header information.
            'ns': 1,
            'nbndskip': 0,
            'nbnd': self.nbnd_xct,
            'nocc': 0,
            'nmode': self.nmodes,
            'nQ': self.nQ,
            'nq': self.nq,
            'Qpts': self.Qpts,
            'qpts': self.qpts,

            # Q+q mappings.
            'Q_plus_q_map': self.k_plus_q_map,
            'Q_minus_q_map': self.k_minus_q_map,

            # energies, frequencies, and matrix elements.
            'energies': self.energies[:self.nbnd_xct, :],
            'frequencies': self.frequencies,
            'xctph_eh' : self.gQq_eh,
            'xctph_e' : self.gQq_e,
            'xctph_h' : self.gQq_h,
        }

        # # Serial version:
        # with h5py.File('xctph.h5', 'w') as f:
        #     for name, data in xctph_dict.items():
        #         f.create_dataset(name, data=data)

        # Parallel version.
        with h5py.File('xctph.h5', 'w', driver='mpio', comm=self.comm) as f:
            # Write everything except the xctph data array, as that needs to be written in parallel.
            for name, data in xctph_dict.items():
                if 'xctph' in name:
                    # Write the xctph array in parallel.
                    ds_xctph_linear = f.create_dataset(f'{name}_linear', shape=(self.nbnd_xct*self.nbnd_xct, self.nQ, self.nmodes, self.nq), dtype=self.gQq_eh.dtype)
                    ds_xctph_linear[self.xct_start:self.xct_end, ...] = data

                    # # Create virtual dataset for reshape.
                    layout = h5py.VirtualLayout(shape=(self.nbnd_xct, self.nbnd_xct, self.nQ, self.nmodes, self.nq), dtype='c16')
                    source = h5py.VirtualSource('xctph.h5', f'{name}_linear', shape=(self.nbnd_xct*self.nbnd_xct, self.nQ, self.nmodes, self.nq), dtype='c16')

                    layout[:, :, :, :, :] = source[:, :, :, :]
                    ds_vx = f.create_virtual_dataset(f'{name}', layout)
                else:
                    f.create_dataset(name, data=data)


        # # # Reshape only on main node.
        # if self.xctbnd_parsize.mpi_rank==0:
        #     with h5py.File('xctph.h5', 'a') as w:
        #         xctph = w['xctph_linear'][:].reshape(self.nbnd_xct, self.nbnd_xct, self.nQ, self.nmodes, self.nq)
        #         del w['xctph_linear']
        #         w.create_dataset('xctph', data=xctph)

        self.comm.Barrier()

#endregion