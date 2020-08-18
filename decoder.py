import sys
from node import Node

class Decoder():
    def __init__(self, encoded_file):
        self.encoded_file = encoded_file
        self.uncompressed_length = 0
        self.tree_info = ""
        self.compressed_data = ""
        self.root = None
    
    def read_in_file_data(self):
        f = open(self.encoded_file, "rb")
        bytes_in_file = f.read()
        try:
            tree_byte_length = int.from_bytes(bytes_in_file[0:4], "big")
            self.uncompressed_length = int.from_bytes(bytes_in_file[4:8], "big")
        except ValueError:
            print("Compressed file is incorrectly formatted")
            return
        try:
            tree_bytes = bytes_in_file[8:(8 + tree_byte_length)]
        except ValueError:
            print("Error trying to decode tree")
            return 
        for compressed_byte in tree_bytes:
            self.tree_info += format(compressed_byte, "08b")
        for compressed_byte in bytes_in_file[(8 + tree_byte_length):]:
            self.compressed_data += format(compressed_byte, "08b")
        f.close()

    def decode_tree_string(self):
        if self.tree_info == "":
            print("No tree bit string to write tree info")
            return
        converted_tree = []
        i = 0
        while i < len(self.tree_info):
            if self.tree_info[i] == "0":
                converted_tree.append("0")
                i += 1
            elif self.tree_info[i] == "1":
                converted_tree.append("1")
                i += 1
                new_byte = self.tree_info[i:i + 8]
                converted_tree.append(int(new_byte, 2).to_bytes(1, "big"))
                i += 8
        self.tree_info = converted_tree

    def construct_tree(self):
        if self.tree_info == "":
            print("No tree data to construct tree")
            return
        node_stack = []
        for i in range(len(self.tree_info)):
            if self.tree_info[i] == "1":
                node_stack.append(Node(value = self.tree_info[i+1]))
            elif self.tree_info[i] == "0":
                if len(node_stack) == 1:
                    break
                parent_node = Node()
                parent_node.right_child = node_stack.pop()
                parent_node.left_child = node_stack.pop()
                node_stack.append(parent_node)
        self.root = node_stack.pop()
        

    def decode_data(self):
        if (self.compressed_data == ""):
            print("No data to decode")
            return
        if self.root is None:
            print("No tree with which to decode data")
            return
        decoded_bytes = []
        searcher = self.root
        counter = 0
        for step in self.compressed_data:
            if counter >= self.uncompressed_length:
                break
            if step == "0":
                searcher = searcher.left_child
            else:
                searcher = searcher.right_child
            if searcher is None:
                break
            if searcher.value is not None:
                decoded_bytes.append(searcher.value)
                searcher = self.root
                counter += 1
        return decoded_bytes
    
    def write_data(self, write_data):
        wf = open("output.txt", "xb")
        for write_byte in write_data:
            wf.write(write_byte)
        wf.close()

    


check = Decoder("output.data")
check.read_in_file_data()
check.decode_tree_string()
check.construct_tree()
decoded = check.decode_data()
check.write_data(decoded)
