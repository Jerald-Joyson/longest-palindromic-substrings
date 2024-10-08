#include <iostream>
using namespace std;

int main() {
    int n;
    long long factorial = 1;

    cout << "Enter a number: ";
    cin >> n;

    if (n < 0) {
        cout << "doesn't exist.";
    } else {
        for (int i = 1; i <= n; ++i) {
            factorial = factorial * i;
        }
        cout << factorial << endl;
    }

    return 0;
}
