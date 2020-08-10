import sys
import heapq
import struct
from node import Node
    

class Encoder():
    def __init__(self):
        self.encodings = {}
        self.tree_string = ""

    def get_frequencies(self, file):
        frequencies = {}
        f = open(file)
        bytes_in_file = f.read()
        for byte_to_process in bytes_in_file:
            if byte_to_process in frequencies:
                frequencies[byte_to_process] += 1
            else:
                frequencies[byte_to_process] = 1
        f.close()
        return frequencies
    
    def generate_tree(self, frequencies):
        frequency_heap = []
        for char in frequencies:
            new_node = Node(char)
            priority_grouping = [frequencies[char], 0, char, new_node]
            frequency_heap.append(priority_grouping)
        heapq.heapify(frequency_heap)
        count = 0
        while len(frequency_heap) > 1:
            parent_node = Node()
            left_child = heapq.heappop(frequency_heap)
            right_child = heapq.heappop(frequency_heap)
            parent_node.left_child = left_child[3]
            parent_node.right_child = right_child[3]
            parent_priority_grouping = [(left_child[0] + right_child[0]), 1, count, parent_node]
            heapq.heappush(frequency_heap, parent_priority_grouping)
            count += 1
        root = heapq.heappop(frequency_heap)
        return root[3] 
    
    def find_char_encoding(self, root, current_path):
        if root is None:
            return
        if root.value is not None:
            self.encodings[root.value] = current_path
        self.find_char_encoding(root.left_child, current_path + "0")
        self.find_char_encoding(root.right_child, current_path + "1")

    def write_compressed_file_data(self, file):
        if self.encodings == {}:
            print("No encodings to use for compression")
            return
        if self.tree_string == "":
            print("Tree has not been stored")
            return
        f = open(file, "r")
        bytes_in_file = f.read()
        data_bytes = []
        write_byte = ""
        compressed_data = ""
        wf = open('output.data', 'xb')
        
    
        for byte_to_write in bytes_in_file:
            byte_encoding = self.encodings[byte_to_write]
            write_byte += byte_encoding
            while len(write_byte) >= 8:
                new_byte = write_byte[0:8]
                data_bytes.append((int(new_byte, 2).to_bytes(1, "big")))
                if len(write_byte) > 8:
                    write_byte = write_byte[8:]
                else:
                    write_byte = ""
        if write_byte != "":
            while len(write_byte) < 8:
                write_byte += "0"
            data_bytes.append((int(write_byte, 2).to_bytes(1, "big")))
        
        self.tree_string += "0"
        # wf.write(len(data_bytes).to_bytes(4, "big"))
        wf.write(len(self.tree_string).to_bytes(4, "big"))
        wf.write(len(bytes_in_file).to_bytes(4, "big"))
        encoded_string = self.tree_string.encode()
        wf.write(encoded_string)
        for data_byte in data_bytes:
            wf.write(data_byte)
        wf.close()
        f.close()

        
    def encode_header_tree(self, root):
        if root is None:
            return
        self.encode_header_tree(root.left_child)
        self.encode_header_tree(root.right_child)
        if root.value is not None:
            self.tree_string += ("1" + root.value)
        else:
            self.tree_string += "0"


def main():
    enc = Encoder()
    histogram = enc.get_frequencies(sys.argv[1])
    tree = enc.generate_tree(histogram)
    enc.find_char_encoding(tree, "")
    enc.encode_header_tree(tree)
    enc.write_compressed_file_data(sys.argv[1])

    

if __name__ == "__main__":
    main()