// re_stack_overflow.cpp - Бесконечная рекурсия
#include <iostream>
using namespace std;

void infinite_recursion(int x) {
    // Нет условия выхода
    infinite_recursion(x + 1);
}

int main() {
    int n;
    cin >> n;

    infinite_recursion(0);

    long long sum = 0;
    for(int i = 0; i < n; i++) {
        int x;
        cin >> x;
        sum += x;
    }

    cout << sum << endl;
    return 0;
}