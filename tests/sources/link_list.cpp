#include <iostream>

class LinkedList {
private:
    struct Node {
        int data;
        Node* next;
    };

public:
    void append(int data) {
        Node* newNode = new Node();
        newNode->data = data;
        newNode->next = nullptr;

        if (head == nullptr) {
            head = newNode;
            tail = newNode;
        } else {
            tail->next = newNode;
            tail = newNode;
        }
    }

    void printList() {
        Node* temp = head;
        while (temp != nullptr) {
            std::cout << temp->data << " ";
            temp = temp->next;
        }
        std::cout << std::endl;
    }

private:
    Node* head = nullptr;
    Node* tail = nullptr;
};

int main() {
    LinkedList list;
    list.append(1);
    list.append(2);
    list.append(3);

    list.printList(); // Output: 1 2 3

    return 0;
}
// This program defines a simple linked list class in C++ and
// demonstrates how to append elements to the list and print them.
