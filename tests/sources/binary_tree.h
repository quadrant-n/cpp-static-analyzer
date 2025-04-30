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

    void setRootNode(Node* node) { root = node; }

    int getMinValueInRightSubtree(Node* node) {
        if (node == NULL) {
            return INT_MAX;
        }

        int minValue = node->data;
        Node* current = node;

        while (current->right != NULL) {
            minValue = std::min(minValue, current->data);
            current = current->right;
        }

        return minValue;
    }

    void printInorder(Node* node) {
        if (node == NULL) {
            return;
        }

        printInorder(node->left);

        std::cout << "Node with value: " << node->data << std::endl;

        printInorder(node->right);
    }

};

#endif // BINARY_TREE_H
