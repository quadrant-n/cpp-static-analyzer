#ifndef BINARY_TREE_H
#define BINARY_TREE_H

#include <cstddef>

class Node {
public:
    int data;
    Node* left;
    Node* right;

    Node(int value) : data(value), left(NULL), right(NULL) {}
};

class BinaryTree {
private:
    Node* root;

public:
    BinaryTree() : root(NULL) {}

    void setRootNode(Node* node) { this->root = node; }

    int getMinValueInRightSubtree(Node* node);

    void printInorder(Node* node);
};

#endif // BINARY_TREE_H
