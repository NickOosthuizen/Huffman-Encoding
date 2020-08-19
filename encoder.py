import os
import heapq
import struct
from node import Node
    

class Encoder():
    def __init__(self):
        self.encodings = {}
        self.tree = []

    # the frequencies of each byte in file is needed
    # in order to construct a huffman encoding
    def get_frequencies(self, file_name):
        frequencies = {}
        f = open(file_name, "rb")
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
        # take each byte from the file and construct it into a min heap 
        # with the lowest frequency bytes at the top
        for char in frequencies:
            new_node = Node(char)
            priority_grouping = [frequencies[char], 0, char, new_node]
            frequency_heap.append(priority_grouping)
        heapq.heapify(frequency_heap)
        count = 0
        # until there is only 1 node left, take the two lowest frequency bytes
        # and join them to a parent node. This parent node has the combined
        # frequencies of its children and is added to the heap
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
    
    # recursively traverse the tree to get the byte encodings (0 = left, 1 = right)
    def find_byte_encoding(self, root, current_path):
        if root is None:
            return
        if root.value is not None:
            self.encodings[root.value] = current_path
        self.find_byte_encoding(root.left_child, current_path + "0")
        self.find_byte_encoding(root.right_child, current_path + "1")

    def write_compressed_file_data(self, file_name):
        if self.encodings == {}:
            print("No encodings to use for compression")
            return
        if self.tree == []:
            print("Tree has not been stored")
            return

        f = open(file_name, "rb")
        bytes_in_file = f.read()
        data_bytes = []
        write_byte = ""
        
        for byte_to_write in bytes_in_file:
            write_byte += self.encodings[byte_to_write]
            # once a bit string is at least 8 characters long, convert
            # it to a byte to be written
            while len(write_byte) >= 8:
                new_byte = write_byte[0:8]
                data_bytes.append((int(new_byte, 2).to_bytes(1, "big")))
                if len(write_byte) > 8:
                    write_byte = write_byte[8:]
                else:
                    write_byte = ""
        # if the encoding still has empty space, fill with 0s
        if write_byte != "":
            while len(write_byte) < 8:
                write_byte += "0"
            data_bytes.append((int(write_byte, 2).to_bytes(1, "big")))
        
        encoded_tree_bytes = self.header_tree_to_bytes(self.tree)

        base_path, base_file_name = os.path.split(file_name)
        base_file_name = "compressed_" + base_file_name
        new_file_name = os.path.join(base_path, base_file_name)

        wf = open(new_file_name, "xb")
        wf.write(len(encoded_tree_bytes).to_bytes(4, "big"))
        wf.write(len(bytes_in_file).to_bytes(4, "big"))
        for tree_byte in encoded_tree_bytes:
            wf.write(tree_byte)
        for data_byte in data_bytes:
            wf.write(data_byte)
        wf.close()
        f.close()

    # use a post order traversal to convert the tree to a list
    def encode_header_tree(self, root):
        if root is None:
            return
        self.encode_header_tree(root.left_child)
        self.encode_header_tree(root.right_child)
        if root.value is not None:
            self.tree.append("1")
            self.tree.append(root.value)
        else:
            self.tree.append("0")

    # convert the tree to a bit encoding to save space
    def header_tree_to_bytes(self, tree_list):
        if tree_list == []:
            print("tree_string is empty")
            return
        bit_tree_encoding = ""
        char_flag = False
        for character in tree_list:
            if character == "0":
                bit_tree_encoding += "0"
            elif character == "1":
                bit_tree_encoding += "1"
                char_flag = True
            else:
                # get the bit encoding of write_bytes and add it to the bit string
                if char_flag:
                    char_bits = format(character, "08b")
                    bit_tree_encoding += char_bits
                    char_flag = False
                else:
                    print("tree was not formatted correctly")
                    return
        tree_bytes = []

        # convert the bit string to bytes that will be written to the output file
        while len(bit_tree_encoding) > 8:
            new_byte = bit_tree_encoding[0:8]
            tree_bytes.append(int(new_byte, 2).to_bytes(1, "big"))
            bit_tree_encoding = bit_tree_encoding[8:]
        if bit_tree_encoding != "":
            while len(bit_tree_encoding) < 8:
                bit_tree_encoding += "0"
            tree_bytes.append(int(bit_tree_encoding, 2).to_bytes(1, "big"))
        return tree_bytes
    
    def encode_and_write_file(self, file_name):
        histogram = self.get_frequencies(file_name)
        tree = self.generate_tree(histogram)
        self.find_byte_encoding(tree, "")
        self.encode_header_tree(tree)
        self.write_compressed_file_data(file_name)

