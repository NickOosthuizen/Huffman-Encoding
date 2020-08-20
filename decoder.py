import os
from node import Node

class Decoder():
    def __init__(self):
        self.uncompressed_length = 0
        self.tree_info = ""
        self.compressed_data = ""
        self.root = None
    
    def read_in_file_data(self, file_name):
        f = open(file_name, "rb")
        bytes_in_file = f.read()
        # compressed files follow an expected format
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

    # get the tree from the encoded bit string
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
                # the 8 bits following a 1 are a write byte
                converted_tree.append(int(new_byte, 2).to_bytes(1, "big"))
                i += 8
        self.tree_info = converted_tree

    # push characters from the tree onto a stack when a one is encountered
    # once a zero is encountered, create a parent node with the top 2 stack 
    # nodes as its children and append the parent to the stack
    # continue until 1 node remains
    def construct_tree(self):
        if self.tree_info == "":
            print("No tree data to construct tree")
            return
        node_stack = []
        for i in range(len(self.tree_info)):
            if self.tree_info[i] == "1":
                node_stack.append(Node(value = self.tree_info[i+1]))
            elif self.tree_info[i] == "0":
                # the tree is complete when there is only 1 node on the stack
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
            # a 0 represents a left, and a 1 represents a right
            if step == "0":
                searcher = searcher.left_child
            else:
                searcher = searcher.right_child
            if searcher is None:
                break
            # if the node has a value, the algorithm has found a write value
            if searcher.value is not None:
                decoded_bytes.append(searcher.value)
                searcher = self.root
                counter += 1
        return decoded_bytes
    
    def write_data(self, write_data, file_name):
        base_path, base_file_name = os.path.split(file_name)
        if len(base_file_name) >= 10 and base_file_name[0:11] == "compressed_":
            base_file_name = "de" + base_file_name
        else:
            base_file_name = "decompressed_" + base_file_name
        new_file_name = os.path.join(base_path, base_file_name)

        wf = open(new_file_name, "xb")
        for write_byte in write_data:
            wf.write(write_byte)
        wf.close()
    
    def decode_and_write_file(self, file_name):
        self.read_in_file_data(file_name)
        self.decode_tree_string()
        self.construct_tree()
        decoded_data = self.decode_data()
        self.write_data(decoded_data, file_name)

