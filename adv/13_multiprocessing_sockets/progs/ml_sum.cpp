#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;

    // Выделяем 1 ГБ памяти (превысит лимит)
    // int весит 4 байта, 300 миллионов * 4 = 1.2 ГБ
    vector<int> huge_array(300000000);

    long long sum = 0;
    for(int i = 0; i < n && i < huge_array.size(); i++) {
        int x;
        cin >> x;
        huge_array[i] = x;
        sum += x;
    }

    cout << sum << endl;
    return 0;
}