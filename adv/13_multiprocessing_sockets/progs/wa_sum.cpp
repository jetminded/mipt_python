// wa_wrong_answer.cpp - Выдает неверный результат
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    long long sum = 0;
    for(int i = 0; i < n; i++) {
        long long x;
        cin >> x;
        sum += x;
    }
    // Ошибка: выводим удвоенную сумму
    cout << sum * 2 << endl;
    return 0;
}