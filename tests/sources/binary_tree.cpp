#include "binary_tree.h"

int main() {
    Node* root = new Node(10);
    root->left = new Node(5);
    root->right = new Node(20);
    root->left->left = new Node(3);
    root->left->right = new Node(7);
    root->right->left = new Node(15);
    root->right->right = new Node(25);
    std::cout << "Inorder traversal of the binary tree:" << std::endl;
    BinaryTree btree;
    btree.setRootNode(root);
    btree.printInorder(root);
    std::cout << "Minimum value in right subtree: " << btree.getMinValueInRightSubtree(root) << std::endl;
    return 0;
}
// This program defines a simple binary tree class in C++ and
// demonstrates how to set the root node, get the minimum value in the right subtree,
// and print the tree in inorder traversal. The main function creates a binary tree,
// sets the root node, and prints the tree in inorder traversal.
// The output will be:
// Node with value: 3
// Node with value: 5
// Node with value: 7
// Node with value: 10
// Node with value: 15
// Node with value: 20
// Node with value: 25
// The program also includes a function to get the minimum value in the right subtree
// of a given node.
