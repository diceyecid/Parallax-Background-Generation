# Used and modified with permission from https://github.com/THU17cyz/GraphCut
import maxflow
import cv2
import numpy as np

from custom_io import debug_out, show_img, write_img
from viz import plot_graph_2d

INF = 1.0e8

class Graph():
    def __init__(self, h, w):
        self.consider_old_seams = True  # whether consider old seams
        self.grad_energy = True  # whether introduce grad into energy func
        self.w, self.h = w, h
        self.filled = np.zeros((self.h, self.w), np.int32)
        self.canvas = np.zeros((self.h, self.w, 3), np.int32)
        self.graph = maxflow.Graph[float]()
        self.node_ids = self.graph.add_grid_nodes((self.h, self.w))
        self.vertical_seams = np.zeros((self.h-1, self.w, 13), np.float64)
        self.horizontal_seams = np.zeros((self.h, self.w-1, 13), np.float64)

    # start from left-top corner
    def init_graph(self, new_patch, new_pattern_size=None):
        h, w = new_patch.shape[:2]
        if new_pattern_size is None:
            new_pattern_size = (new_patch.shape[0], new_patch.shape[1])
        row_rand = np.random.randint(0, h-new_pattern_size[0]+1)
        col_rand = np.random.randint(0, w-new_pattern_size[1]+1)
        new_patch = new_patch[row_rand:row_rand+new_pattern_size[0],
                              col_rand:col_rand+new_pattern_size[1]]
        new_h, new_w = new_patch.shape[:2]
        self.filled[:new_h, :new_w] = 1
        self.canvas[:new_h, :new_w] = new_patch

    # matching cost, fast with summed table and FFT
    def fast_cost_fn(self, new_patch, row_range, col_range):
        new_value = new_patch
        new_h, new_w = new_patch.shape[:2]
        mask = np.expand_dims(self.filled, -1)
        canvas_with_mask = mask*self.canvas

        # summed table for speed up
        summed_table = np.zeros((self.h+1, self.w+1), np.float64)
        summed_table[1:, 1:] = np.power(canvas_with_mask, 2).sum(2)
        summed_table = summed_table.cumsum(axis=0).cumsum(axis=1)
        y_start, x_start = new_h, new_w
        y, x = len(row_range), len(col_range)
        term2 = summed_table[0:y, 0:x] + \
            summed_table[y_start:y_start+y, x_start:x_start+x] - \
            summed_table[y_start:y_start+y, 0:x] - \
            summed_table[0:y, x_start:x_start+x]

        # FFT for speed up
        term3 = cv2.filter2D(canvas_with_mask, -1, new_value, anchor=(0, 0))[0:y, 0:x].sum(axis=2)
        term1 = cv2.filter2D(np.tile(mask, (1, 1, 3)), -1, np.power(new_value, 2), anchor=(0, 0))[0:y, 0:x].sum(axis=2)
 
        # summed table for mask count calculation speed up
        summed_table_mask = np.zeros((self.h+1, self.w+1), np.float64)
        summed_table_mask[1:, 1:] = mask[:, :, 0]
        summed_table_mask = summed_table_mask.cumsum(axis=0).cumsum(axis=1)
        mask_count = summed_table_mask[0:y, 0:x] + \
            summed_table_mask[y_start:y_start+y, x_start:x_start+x] - \
            summed_table_mask[y_start:y_start+y, 0:x] - \
            summed_table_mask[0:y, x_start:x_start+x]
        
        # must cover some area
        cost_table = term1.astype(np.float64)+term2-2*term3
        cost_table = cost_table.astype(np.float64)
        zero_mask = mask_count == 0
        not_zero_mask = np.logical_not(zero_mask)

        cost_table = INF*zero_mask+(cost_table/(mask_count+1e-8))*not_zero_mask
        return cost_table, mask_count

    # matching cost, slow
    def cost_fn(self, new_patch):
        new_t, new_l, new_h, new_w, new_value = new_patch
        new_r, new_b = min(new_l + new_w, self.w), min(new_t + new_h, self.h)
        overlap_area = self.filled[new_t:new_b, new_l:new_r] 
        overlap_count = overlap_area.sum()
        canvas_with_mask = np.expand_dims(overlap_area, -1)*(self.canvas[new_t:new_b, new_l:new_r]-new_value)
        overlap_cost = np.power(canvas_with_mask, 2).astype(np.float64).sum()
        if overlap_count == 0:
            return INF, 0
        overlap_cost /= overlap_count 
        return overlap_cost, overlap_count

    # energy func
    def weight_fn(self, new_value, row_idx, col_idx, new_t, new_l, vertical, 
                  ord=2, eps=1e-8, old_value_1=None, old_value_2=None):
        # could specify old_value
        if old_value_1 is None:
            old_value_1 = self.canvas[row_idx][col_idx]
        if old_value_2 is None:
            old_value_2 = self.canvas[row_idx+1][col_idx] if vertical \
                else self.canvas[row_idx][col_idx+1]
        ws = np.linalg.norm(old_value_1-new_value[row_idx-new_t][col_idx-new_l], ord=ord)
        if vertical:
            wt = np.linalg.norm(
                old_value_2-new_value[row_idx-new_t+1][col_idx-new_l], ord=ord)
            grad_s = np.linalg.norm(old_value_1-old_value_2, ord=ord)
            grad_t = np.linalg.norm(
                new_value[row_idx-new_t][col_idx-new_l]-new_value[row_idx-new_t+1][col_idx-new_l], ord=ord)
        else:
            wt = np.linalg.norm(
                old_value_2-new_value[row_idx-new_t][col_idx-new_l+1], ord=ord)
            grad_s = np.linalg.norm(old_value_1-old_value_2, ord=ord)
            grad_t = np.linalg.norm(
                new_value[row_idx-new_t][col_idx-new_l]-new_value[row_idx-new_t][col_idx-new_l+1], ord=ord)
        w = ws+wt
        # integrate grad into energy function
        if self.grad_energy:
            w /= (grad_s+grad_t)*2+eps
        return w
        
    def create_graph(self, new_patch):
        new_t, new_l, new_h, new_w, new_value = new_patch
        new_r, new_b = new_l + new_w, new_t + new_h
        src_tedge_count = 0
        sink_tedge_count = 0
        nodes = []
        edges = []
        tedges = []
        node_count = self.h*self.w
        for row_idx in range(new_t, new_b):
            for col_idx in range(new_l, new_r):
                # only consider filled pixels
                if not self.filled[row_idx, col_idx]:
                    continue
                if row_idx < new_b - 1 and self.filled[row_idx+1, col_idx]:
                    # add old seam nodes 
                    if self.consider_old_seams and self.vertical_seams[row_idx, col_idx][0] > 0:
                        nodes.append(node_count)
                        weight = self.vertical_seams[row_idx, col_idx, 0]
                        tedges.append((node_count, 0, weight))
                        weight = self.weight_fn(
                            new_value, row_idx, col_idx, new_t, new_l, True, 
                            old_value_1=self.vertical_seams[row_idx, col_idx, 1:4], 
                            old_value_2=self.vertical_seams[row_idx, col_idx, 4:7])
                        edges.append((self.node_ids[row_idx][col_idx],
                                      node_count, weight))
                        weight = self.weight_fn(
                            new_value, row_idx, col_idx, new_t, new_l, True,
                            old_value_1=self.vertical_seams[row_idx, col_idx, 7:10],
                            old_value_2=self.vertical_seams[row_idx, col_idx, 10:13])
                        edges.append((self.node_ids[row_idx+1][col_idx],
                                      node_count, weight))
                        node_count += 1
                    else:
                        weight = self.weight_fn(new_value, row_idx, 
                                                col_idx, new_t, new_l, True)
                        edges.append((self.node_ids[row_idx][col_idx],
                                      self.node_ids[row_idx+1][col_idx],
                                      weight))
                if col_idx < new_r - 1 and self.filled[row_idx, col_idx+1]:
                    if self.consider_old_seams and self.horizontal_seams[row_idx, col_idx][0] > 0:
                        nodes.append(node_count)
                        weight = self.horizontal_seams[row_idx, col_idx, 0]
                        tedges.append((node_count, 0, weight))
                        weight = self.weight_fn(
                            new_value, row_idx, col_idx, new_t, new_l, False,
                            old_value_1=self.horizontal_seams[row_idx, col_idx, 1:4],
                            old_value_2=self.horizontal_seams[row_idx, col_idx, 4:7])
                        edges.append((self.node_ids[row_idx][col_idx],
                                      node_count, weight))
                        weight = self.weight_fn(
                            new_value, row_idx, col_idx, new_t, new_l, False,
                            old_value_1=self.horizontal_seams[row_idx, col_idx, 7:10],
                            old_value_2=self.horizontal_seams[row_idx, col_idx, 10:13])
                        edges.append((self.node_ids[row_idx][col_idx+1],
                                      node_count, weight))
                        node_count += 1
                    else:
                        weight = self.weight_fn(new_value, row_idx, 
                                                col_idx, new_t, new_l, False)
                        edges.append((self.node_ids[row_idx][col_idx], 
                                      self.node_ids[row_idx][col_idx+1],
                                      weight))
                # to new patch (sink)
                if row_idx > new_t and not self.filled[row_idx-1, col_idx] or \
                        row_idx < new_b-1 and not self.filled[row_idx+1, col_idx] or \
                        col_idx > new_l and not self.filled[row_idx, col_idx-1] or \
                        col_idx < new_r-1 and not self.filled[row_idx, col_idx+1]:
                    tedges.append((self.node_ids[row_idx][col_idx], 0, np.inf))
                    src_tedge_count += 1

                # from existing region (source)
                if row_idx == new_t and row_idx > 0 and self.filled[row_idx-1, col_idx] or \
                        row_idx == new_b-1 and row_idx < self.h-1 and self.filled[row_idx+1, col_idx] or \
                        col_idx == new_l and col_idx > 0 and self.filled[row_idx, col_idx-1] or \
                        col_idx == new_r-1 and col_idx < self.w-1 and self.filled[row_idx, col_idx+1]:
                    tedges.append((self.node_ids[row_idx][col_idx], np.inf, 0))
                    sink_tedge_count += 1
        return nodes, edges, tedges

    def match_patch(self, pattern, row=-1, col=-1, mode='random', k=10, new_pattern_size=None):
        if mode == 'opt_sub':
            h, w = pattern.shape[:2]
            if new_pattern_size is None:
                new_pattern_size = (pattern.shape[0]//2, pattern.shape[1]//2)
            row_rand = np.random.randint(0, h-new_pattern_size[0]+1)
            col_rand = np.random.randint(0, w-new_pattern_size[1]+1)
            pattern = pattern[row_rand:row_rand+new_pattern_size[0],
                              col_rand:col_rand+new_pattern_size[1]]
        h, w = pattern.shape[:2]
        max_overlap = max(int(h*w*0.7), h*w-self.h*self.w+self.filled.sum())
        min_overlap = int(h*w*0.1)
        if row == -1 or col == -1:
            if mode == 'random':
                row = np.random.randint(0, self.h-h+1) if row == -1 else row
                col = np.random.randint(0, self.w-w+1) if col == -1 else col
            elif mode == 'opt_whole' or mode == 'opt_sub':
                row_range = list(range(0, self.h-h+1, 1))
                col_range = list(range(0, self.w-w+1, 1))
                cost_table, mask_count = self.fast_cost_fn(pattern, row_range, col_range)
                cost_table_flatten = cost_table.reshape((-1))
                mask_count_flatten = mask_count.reshape((-1))
                valid_mask = (mask_count_flatten <= max_overlap) * \
                    (mask_count_flatten >= min_overlap)
                
                col_num = len(col_range)
                valid_count = valid_mask.sum()
                min_mask_count = mask_count_flatten.min()
                if row != -1:
                    valid_count = valid_mask.reshape((-1, col_num))[row, :].sum()
                    min_mask_count = mask_count_flatten.reshape(
                        (-1, col_num))[row, :].min()
                if col != -1:
                    valid_count = valid_mask.reshape((-1, col_num))[:, col].sum()
                    min_mask_count = mask_count_flatten.reshape(
                        (-1, col_num))[:, col].min()
                if valid_count == 0:
                    p_table_flatten = (
                        mask_count_flatten == min_mask_count).astype(np.float32)
                else:
                    sigma = np.std(pattern.reshape(-1, 3), axis=0)
                    sigma_sqr = (sigma*sigma).sum()
                    p_table_flatten = -cost_table_flatten*k/sigma_sqr
                    p_table_flatten = np.exp(p_table_flatten)
                    p_table_flatten = p_table_flatten*valid_mask
                if row != -1:
                    for idx in range(len(p_table_flatten)):
                        if idx//col_num != row:
                            p_table_flatten[idx] = 0
                if col != -1:
                    for idx in range(len(p_table_flatten)):
                        if idx%col_num != col:
                            p_table_flatten[idx] = 0
                p_table_flatten /= p_table_flatten.sum()
                p_table_flatten = np.cumsum(p_table_flatten)
                rand_num = np.random.rand()
                min_idx = 0
                for i, p in enumerate(p_table_flatten):
                    if rand_num < p:
                        min_idx = i
                        break
                row = min_idx // len(col_range)
                col = min_idx % len(col_range)
            else:
                raise NotImplementedError()

        return (row, col, h, w, pattern)

    # blend new patch and existing
    def blend(self, pattern_info):
        row, col, h, w, pattern = pattern_info
        nodes, edges, tedges = self.create_graph((row, col, h, w, pattern))
        graph = maxflow.Graph[float]()
        final_nodes = graph.add_nodes(len(nodes)+self.h*self.w)
        edge_weights = np.zeros((self.h, self.w, 2))

        debug_out("pattern channels: %i, graph channels: %i\n", pattern.shape[2], self.canvas.shape[2])

        for edge in edges:
            graph.add_edge(edge[0], edge[1], edge[2], edge[2])
            row_, col_ = edge[0]//self.w, edge[0]%self.w
            if edge[1] == edge[0]+1: 
                edge_weights[row_, col_, 1] = edge[2]
            else:
                edge_weights[row_, col_, 0] = edge[2]
        for tedge in tedges:
            graph.add_tedge(tedge[0], tedge[1], tedge[2])

        sgm = graph.get_grid_segments(self.node_ids)
        for row_idx in range(row, row+h):
            for col_idx in range(col, col+w):

                # update the old seams
                if self.consider_old_seams:
                    debug_out("pattern channels: %i, graph channels: %i\n", pattern.shape[2], self.canvas.shape[2])
                    if row_idx < row+h-1 and self.filled[row_idx, col_idx] and self.filled[row_idx+1, col_idx]:
                        if not sgm[row_idx, col_idx] and sgm[row_idx+1, col_idx]:
                            self.vertical_seams[row_idx][col_idx][0] = edge_weights[row_idx][col_idx][0]
                            self.vertical_seams[row_idx][col_idx][1:] = np.concatenate([
                                    self.canvas[row_idx, col_idx],
                                    self.canvas[row_idx+1, col_idx],
                                    pattern[row_idx-row, col_idx-col],
                                    pattern[row_idx-row+1, col_idx-col]
                                ], axis=-1)
                        if sgm[row_idx, col_idx] and not sgm[row_idx+1, col_idx]:
                            self.vertical_seams[row_idx][col_idx][0] = edge_weights[row_idx][col_idx][0]
                            self.vertical_seams[row_idx][col_idx][1:] = np.concatenate([
                                    pattern[row_idx-row, col_idx-col],
                                    pattern[row_idx-row+1, col_idx-col],
                                    self.canvas[row_idx, col_idx],
                                    self.canvas[row_idx+1, col_idx],
                                ], axis=-1)
                    
                    if col_idx < col+w-1 and self.filled[row_idx, col_idx] and self.filled[row_idx, col_idx+1]:
                        if not sgm[row_idx, col_idx] and sgm[row_idx, col_idx+1]:
                            self.horizontal_seams[row_idx][col_idx][0] = edge_weights[row_idx][col_idx][1]
                            self.horizontal_seams[row_idx][col_idx][1:] = np.concatenate([
                                    self.canvas[row_idx, col_idx],
                                    self.canvas[row_idx, col_idx+1],
                                    pattern[row_idx-row, col_idx-col],
                                    pattern[row_idx-row, col_idx-col+1]
                                ], axis=-1)
                        if sgm[row_idx, col_idx] and not sgm[row_idx, col_idx+1]:
                            self.horizontal_seams[row_idx][col_idx][0] = edge_weights[row_idx][col_idx][1]
                            self.horizontal_seams[row_idx][col_idx][1:] = np.concatenate([
                                    pattern[row_idx-row, col_idx-col],
                                    pattern[row_idx-row, col_idx-col+1],
                                    self.canvas[row_idx, col_idx],
                                    self.canvas[row_idx, col_idx+1]
                                ], axis=-1)
                    
                if not self.filled[row_idx, col_idx] or self.filled[row_idx, col_idx] and sgm[row_idx, col_idx]:
                        self.canvas[row_idx, col_idx] = pattern[row_idx-row, col_idx-col]
        self.filled[row:row+h, col:col+w] = 1

    def show_canvas(self):
        show_img(self.canvas)
    
    def write_canvas(self, fn):
        write_img(self.canvas, fn)


if __name__ == '__main__':   
    g = Graph(10, 10)
    g.init_graph(np.ones((5, 5, 3), np.int32)*2) 
    nodes, edges, tedges = g.create_graph((2, 2, 5, 5, np.zeros((5, 5, 3)).astype(np.int32)))
    graph = maxflow.Graph[float]()
    nodes = graph.add_grid_nodes((g.h, g.w))
    for edge in edges:
        graph.add_edge(edge[0], edge[1], edge[2], edge[2])
    for tedge in tedges:
        graph.add_tedge(tedge[0], tedge[1], tedge[2])
    plot_graph_2d(graph, (10, 10)) 