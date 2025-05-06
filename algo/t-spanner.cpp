#include <bits/stdc++.h>

using namespace std;

int n, m, t;

struct edge
{
    int v, w, s, oi;
    // opposite vertex, weight, status, index in opposite list
    // status 0 -> removed
    // status 1 -> possible
    // status 2 -> in spanner
};

// Timer macros
#define TIMER_START(name) auto timer_##name##_start = std::chrono::high_resolution_clock::now()
#define TIMER_END(name) auto timer_##name##_end = std::chrono::high_resolution_clock::now()
#define TIMER_PRINT(name) cerr << \
    std::chrono::duration_cast<std::chrono::microseconds>( \
    timer_##name##_end - timer_##name##_start).count() << endl


vector<vector<edge>> adj(0);

mt19937_64 RNG(chrono::steady_clock::now().time_since_epoch().count());

const int INF = (int)1e9;

bool sample(int n, int k)
{
    // 1/n^*(1/k) chance
    uniform_real_distribution<double> dist(0.0, 1.0);
    double vl = dist(RNG);
    double exp = - (1.0/(double)k);
    double sp = pow(n, exp);
    return vl<=sp;
}

signed main()
{
    // freopen("debug.log", "w", stderr);
    TIMER_START(tt);
    ios::sync_with_stdio(0);
    cin.tie(0);

    cin>>n>>m>>t; // take parameters
    adj.resize(n);

    int k = (t+1)/2;

    for(int i=0; i<m; i++)
    {
        int u, v, w;
        cin>>u>>v>>w;
        edge eu, ev;
        eu.w = ev.w = w;
        eu.s = ev.s = 1;
        eu.oi = adj[v].size();
        ev.oi = adj[u].size();
        eu.v = v;
        ev.v = u;
        adj[v].push_back(ev);
        adj[u].push_back(eu);
    }

    TIMER_START(total);

    vector<int> cluster(n, 0);
    vector<int> is_center(n, 0);
    vector<int> centers(0);
    vector<int> ivd(n, 1);
    // fill(ivd.begin(), ivd.end(), 1);
    iota(cluster.begin(), cluster.end(), 0);
    for(int i=0; i<n; i++)
    {
        centers.push_back(i);
    }

    // phase 1
    TIMER_START(phase1);
    for(int i=1; i<k; i++)
    {
        // step 1
        // sampling
        fill(is_center.begin(), is_center.end(), 0);
        int cc = 0;
        for(auto j: centers)
        {
            if(sample(n, k))
            {
                is_center[j] = 1;
                cc++;
            }
        }
        if(!cc) is_center[centers[0]] = 1;
        // cerr<<cc<<"\n";
        // cerr<<"centers: ";
        // for(int i=0; i<n; i++)
        // {
        //     if(is_center[i]) cerr<<i<<" ";
        // }
        // cerr<<"\n";

        // step 2
        vector<int> min_idx(n, -1); 
        for(int j=0; j<n; j++)
        {
            if(!ivd[j]) continue;
            if(is_center[cluster[j]]) continue;
            int mw = INF;
            for(int k=0; k<adj[j].size(); k++)
            {
                auto& e = adj[j][k];
                if(!e.s) continue;
                if(!is_center[cluster[e.v]]) continue;
                if(e.w<mw)
                {
                    mw = e.w;
                    min_idx[j] = k;
                }
            }
        }

        //step 3
        vector<int> center_idx(n, -1);
        int cidx = 0;
        for(auto j: centers)
        {
            center_idx[j] = cidx;
            cidx++;
        }
        vector<pair<int, int>> to_add(0);
        vector<pair<int, int>> to_rem(0);
        vector<pair<int, int>> cluster_change(0);
        for(int j=0; j<n; j++)
        {
            if(!ivd[j]) continue;
            if(is_center[cluster[j]]) continue;
            if(min_idx[j]==-1)
            {
                vector<int> min_ed(cidx, -1);
                for(int k=0; k<adj[j].size(); k++)
                {
                    auto & e = adj[j][k];
                    if(e.s!=1) continue;
                    to_rem.push_back({j, k});
                    if(center_idx[cluster[e.v]]<0) continue;
                    int ci = center_idx[cluster[e.v]];
                    if(min_ed[ci]==-1)
                    {
                        min_ed[ci] = k;
                    }
                    else if(e.w<adj[j][min_ed[ci]].w)
                    {
                        min_ed[ci] = k;
                    }
                }
                ivd[j] = 0;
                for(int k=0; k<cidx; k++)
                {
                    if(min_ed[k]<0) continue;
                    to_add.push_back({j, min_ed[k]});
                }
            }
        }
        for(int j=0; j<n; j++)
        {
            if(!ivd[j]) continue;
            if(is_center[cluster[j]]) continue;
            if(min_idx[j]!=-1)
            {
                int ncj = cluster[adj[j][min_idx[j]].v];
                vector<int> min_ed(cidx, -1);
                vector<int> tr(cidx, 0);
                for(int k=0; k<adj[j].size(); k++)
                {
                    auto & e = adj[j][k];
                    if(e.s!=1) continue;
                    // if(!is_center[cluster[e.v]]) to_rem.push_back({j, k});
                    if(cluster[e.v]==ncj) to_rem.push_back({j, k});
                    if(center_idx[cluster[e.v]]<0) continue;
                    int ci = center_idx[cluster[e.v]];
                    if(min_ed[ci]==-1)
                    {
                        min_ed[ci] = k;
                    }
                    else if(e.w<adj[j][min_ed[ci]].w)
                    {
                        min_ed[ci] = k;
                    }
                    if(e.w<adj[j][min_idx[j]].w && ci!=center_idx[ncj])
                    {
                        tr[ci] = 1;
                    }
                }
                cluster_change.push_back({j, ncj});
                int cw = adj[j][min_idx[j]].w;
                for(int k=0; k<cidx; k++)
                {
                    // if(is_center[centers[k]]) continue;
                    if(min_ed[k]<0) continue;
                    if(adj[j][min_ed[k]].w>=cw) continue;
                    to_add.push_back({j, min_ed[k]});
                }
                to_add.push_back({j, min_idx[j]});
                for(int k=0; k<adj[j].size(); k++)
                {
                    auto & e = adj[j][k];
                    if(e.s!=1) continue;
                    int ci = center_idx[cluster[e.v]];
                    if(tr[ci]) to_rem.push_back({j, k});
                }
            }
        }
        for(auto p: to_add)
        {
            auto & e = adj[p.first][p.second];
            e.s = 2;
            adj[e.v][e.oi].s = 2;
        }
        for(auto p: to_rem)
        {
            auto & e = adj[p.first][p.second];
            if(e.s==2) continue;
            e.s = 0;
            adj[e.v][e.oi].s = 0;
        }
        for(auto p: cluster_change)
        {
            cluster[p.first] = p.second;
        }
        

        //step 4
        for(int j=0; j<n; j++)
        {
            if(!is_center[cluster[j]]) continue;
            for(auto& e: adj[j])
            {
                if(cluster[e.v]!=cluster[j]) continue;
                if(e.s<2) e.s = 0;
            }
        }

        centers.clear();
        for(int j=0; j<n; j++)
        {
            if(is_center[j]) centers.push_back(j);
        }
    }

    TIMER_END(phase1);

    // cerr<<"After ph1:\n";
    // for(int i=0; i<n; i++)
    // {
    //     for(auto j: adj[i])
    //     {
    //         if(j.s==2)
    //         {
    //             cerr<<i<<" "<<j.v<<" "<<j.w<<"\n";
    //         }
    //     }
    // }

    TIMER_START(phase2);
    //phase 2
    vector<pair<int, int>> to_add(0);
    vector<pair<int, int>> to_rem(0);

    vector<int> center_idx(n, -1);
    int cidx = 0;
    for(auto i: centers)
    {
        center_idx[i] = cidx;
        cidx++;
    }
    for(int i=0; i<n; i++)
    {
        if(!ivd[i]) continue;
        vector<int> min_ed(cidx, -1);
        for(int j=0; j<adj[i].size(); j++)
        {
            auto & e = adj[i][j];
            if(e.s!=1) continue;
            if(center_idx[cluster[e.v]]<0) continue;
            to_rem.push_back({i, j});
            int ci = center_idx[cluster[e.v]];
            if(min_ed[ci]==-1)
            {
                min_ed[ci] = j;
            }
            else
            {
                if(e.w<adj[i][min_ed[ci]].w) min_ed[ci] = j;
            }
        }
        for(int j=0; j<cidx; j++)
        {
            if(min_ed[j]<0) continue;
            to_add.push_back({i, min_ed[j]});
        }
    }

    for(auto p: to_add)
    {
        auto & e = adj[p.first][p.second];
        e.s = 2;
        adj[e.v][e.oi].s = 2;
    }
    for(auto p: to_rem)
    {
        auto & e = adj[p.first][p.second];
        if(e.s==2) continue;
        e.s = 0;
        adj[e.v][e.oi].s = 0;
    }
    TIMER_END(phase2);

    vector<pair<pair<int, int>, int>> fin(0);
    for(int i=0; i<n; i++)
    {
        for(auto & e: adj[i])
        {
            if(e.v<i) continue;
            if(e.s<2) continue;
            // cout<<i<<" "<<e.v<<" "<<e.w<<"\n";
            fin.push_back({{i, e.v}, e.w});
        }
    }
    TIMER_END(total);
    // cerr <<" TIMERS: " << timer_phase1_start.time_since_epoch().count() << " " << timer_phase1_end.time_since_epoch().count() << " " << timer_phase2_start.time_since_epoch().count() << " " << timer_phase2_end.time_since_epoch().count() << " " << timer_total_start.time_since_epoch().count() << " " << timer_total_end.time_since_epoch().count() << "\n";
    // Calculate time differences in milliseconds
    auto phase1_ms = std::chrono::duration_cast<std::chrono::microseconds>(timer_phase1_end - timer_phase1_start).count();
    auto phase2_ms = std::chrono::duration_cast<std::chrono::microseconds>(timer_phase2_end - timer_phase2_start).count();
    auto total_ms = std::chrono::duration_cast<std::chrono::microseconds>(timer_total_end - timer_total_start).count();

    // Print time taken for each phase
    cerr << phase1_ms << endl;
    cerr << phase2_ms << endl;
    cerr << total_ms << endl;

    cout<<n<<" "<<fin.size()<<"\n";
    for(auto e: fin)
    {
        cout<<e.first.first<<" "<<e.first.second<<" "<<e.second<<"\n";
    }
    TIMER_END(tt);
    TIMER_PRINT(tt);
    return 0;
}