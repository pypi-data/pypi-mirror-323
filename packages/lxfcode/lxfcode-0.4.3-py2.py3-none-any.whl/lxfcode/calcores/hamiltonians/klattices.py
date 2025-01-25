import numpy as np

__all__ = ["BiKLattices", "TriKLatticesIncommensurate"]


class BiKLattices:
    def __init__(self, shells=7, twist_layer=2, res_layer=None) -> None:
        self.shells = shells
        self.twist_layer = twist_layer
        self.res_layer = res_layer

    def expand_vecs(self):
        twist_diff = self.twist_layer - 1
        expand_v = np.array(
            [[0, 0, twist_diff], [1, 0, twist_diff], [0, 1, twist_diff]]
        )
        return expand_v

    def basis_set(self):
        v0 = np.array([[0, 0, 1]])
        v1_list = [v0]
        v2_list = []
        expand_v = self.expand_vecs()
        to_v1 = False
        while self.shells > 0:
            self.shells -= 1
            if to_v1:
                tmp_vecs = np.kron(v2_list[-1], np.ones((3, 1))) - np.kron(
                    np.ones((len(v2_list[-1]), 1)), expand_v
                )

                tmp_vecs = np.unique(tmp_vecs, axis=0)
                v1_list.append(tmp_vecs)
            else:
                tmp_vecs = np.kron(v1_list[-1], np.ones((3, 1))) + np.kron(
                    np.ones((len(v1_list[-1]), 1)), expand_v
                )

                tmp_vecs = np.unique(tmp_vecs, axis=0)
                v2_list.append(tmp_vecs)
            to_v1 = not to_v1
        v1_list = np.unique(np.vstack(v1_list), axis=0)
        v2_list = np.unique(np.vstack(v2_list), axis=0)

        if self.res_layer is not None:
            res_diff = self.res_layer - 1
            v3_list = v1_list.copy()
            v3_list[:, -1] += res_diff
            return v1_list, v2_list, v3_list

        return v1_list, v2_list


class TriKLatticesIncommensurate:
    def __init__(self, shells=7, middle_lindex=2, res_layer=None) -> None:
        self.shells = shells
        self.m_lindex = middle_lindex
        self.res_layer = res_layer

    def expand_vecs(self):
        l_diff = 1
        expand_v = np.array([[0, 0, l_diff, 0], [1, 0, l_diff, 0], [0, 1, l_diff, 0]])
        return expand_v

    def basis_set(self):
        v0 = np.array([[0, 0, 2, 2]])

        v_m_list = [v0]
        v_t_list = []
        v_b_list = []

        expand_v = self.expand_vecs()

        to_midlle = False

        while self.shells > 0:
            self.shells -= 1

            if to_midlle:
                t2m = np.kron(v_t_list[-1], np.ones((3, 1))) - np.kron(
                    np.ones((len(v_t_list[-1]), 1)), expand_v
                )

                b2m = np.kron(v_b_list[-1], np.ones((3, 1))) - np.kron(
                    np.ones((len(v_b_list[-1]), 1)), expand_v
                )

                t2m = np.unique(t2m, axis=0)
                b2m = np.unique(b2m, axis=0)

                v_m_list.append(t2m)
                v_m_list.append(b2m)
            else:
                ##  Middle to top
                m2t = np.kron(v_m_list[-1], np.ones((3, 1))) + np.kron(
                    np.ones((len(v_m_list[-1]), 1)), expand_v
                )
                m2t[:, -1] = 1

                ##  Middle to bottom
                m2b = np.kron(v_m_list[-1], np.ones((3, 1))) + np.kron(
                    np.ones((len(v_m_list[-1]), 1)), expand_v
                )
                m2b[:, -1] = 3

                ##  Get unique vectors
                # print("m to t before: ", len(m2t))
                m2t = np.unique(m2t, axis=0)
                # print("m to t after: ", len(m2t))

                # print("m to b before: ", len(m2b))
                m2b = np.unique(m2b, axis=0)
                # print("m to b after: ", len(m2b))

                v_t_list.append(m2t)
                v_b_list.append(m2b)

            to_midlle = not to_midlle
        v_m_list = np.unique(np.vstack(v_m_list), axis=0)
        v_t_list = np.unique(np.vstack(v_t_list), axis=0)
        v_b_list = np.unique(np.vstack(v_b_list), axis=0)

        return v_m_list, v_t_list, v_b_list

    def plot_dots(self, angle1, angle2):
        vm_list, vt_list, vb_list = self.basis_set()

        theta1 = angle1 * np.pi / 180
        theta2 = angle2 * np.pi / 180

        rot_m1 = np.array(
            [[np.cos(theta1), -np.sin(theta1)], [np.sin(theta1), np.cos(theta1)]]
        )

        pass
