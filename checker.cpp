#include "bits/stdc++.h"
using namespace std;
/*
#include <ext/pb_ds/assoc_container.hpp>
using namespace __gnu_pbds;
using ordered_set = tree<int, null_type, less<int>, rb_tree_tag, tree_order_statistics_node_update>;
*/

#define all(x) begin(x), end(x)
#define rall(x) rbegin(x), rend(x)
#define sz(x) (int)(x).size()

using ll = long long;
#define int ll
const int mod = 1e9+7;

vector<vector<int>> distances_fw(int n, vector<vector<pair<int, int>>> &adj) {
    vector<vector<int>> dist(n, vector<int>(n, (1LL<<50)));
    for (int u = 0; u < n; ++u) {
        dist[u][u] = 0;
        for (auto [v, w] : adj[u]) {
            dist[u][v] = min(dist[u][v], w);
        }
    }
    for (int k = 0; k < n; ++k)
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j)
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
    return dist;
}

bool verify(const vector<vector<int>> &dist1, const vector<vector<int>> &dist2, int threshold) {
    int n = dist1.size();
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            if (dist2[i][j] > dist1[i][j] * threshold)
                return false;
    return true;
}

void solve(int tc) {
    vector<vector<pair<int, int>>> adj1, adj2;
    int n, m_o, threshold;
    cin >> n >> m_o >> threshold;
    adj1.resize(n);
    adj2.resize(n);
    for (int i = 0; i < m_o; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        adj1[u].push_back({v, w});
        adj1[v].push_back({u, w});
    }
    vector<vector<int>> dist1 = distances_fw(n, adj1);
    int m_2;
    cin >> n >> m_2;
    for (int i = 0; i < m_2; ++i) {
        int u, v, w;
        cin >> u >> v >> w;
        adj2[u].push_back({v, w});
        adj2[v].push_back({u, w});
    }
    vector<vector<int>> dist2 = distances_fw(n, adj2);

    cout << (verify(dist1, dist2, threshold) ? "YES" : "NO") << '\n';
}

signed main() {
    cin.tie(0)->sync_with_stdio(0);
    int tc = 1;
    //cin >> tc;
    for (int i = 1; i <= tc; ++i) solve(i);
    return 0;
}

