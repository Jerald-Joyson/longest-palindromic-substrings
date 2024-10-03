// find the longest palindromic substring in a given string.

// I am less aware about the typescript, so I have done the above problem in C++


#include <iostream>
#include <string>
#include <unordered_set>

using namespace std;


void printSubstrings(const string& str) {
    int n = str.length();
    unordered_set<string> pali;
    for (int i=0; i<n; i++) {
        for (int len=1; len <= n-i; len++) {
            string sub;
            for (int j=0; j<len; j++) {
                sub = sub + str[i+j];
            }
            bool isPalindrome = true;
            for (int j=0; j < len/2; j++) {
                if (sub[j] != sub[len - j - 1]) {
                    isPalindrome = false;
                    break;
                }
            }
            if (isPalindrome) {
                pali.insert(sub);
            }
        }
    }
    int largest = 0;
    for (auto it = pali.begin(); it != pali.end(); ++it) {
        if (it->length() > largest) {
            largest = it->length();
        }
    }
    for (auto it = pali.begin(); it != pali.end();) {
        if (it->length() != largest) {
            it = pali.erase(it);
        } else {
            cout << *it << endl;
            ++it;
        }
    }
}

int main() {
    string str;
    cout << "Enter a string: ";
    cin >> str;

    cout << "longest palindromic substrings are:\n";
    printSubstrings(str);

    return 0;
}


