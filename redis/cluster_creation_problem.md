
docker exec -it poc_redis-node1_1 redis-cli --cluster create poc_redis-node1_1:6379 poc_redis-node2_1:6380 poc_redis-node3_1:6381 --cluster-replicas 0
>>> Performing hash slots allocation on 3 nodes...
でずっと返答が返ってこなくなりました。調査方法はありますか？

`Waiting for the cluster to join`の状態で停止する問題は、Redisノード間での通信が一見正常に見えても、クラスタ構成に必要な特定の設定が不足している場合に発生することがあります。以下に考えられる原因とその解決策を示します。

---

## **1. 主な原因**
### **1.1. クラスタ構成に必要なポート（クラスタバスポート）が開いていない**
Redis Clusterでは、データ操作用ポート（例: 6379, 6380, 6381）だけでなく、**クラスタバスポート**（デフォルトでデータ操作用ポート+10000）が必要です。このポートが開いていないと、ノード間でのクラスタ通信が正常に行えず、クラスタが作成できません。

---

## **2. 解決方法**

### **2.1. クラスタバスポートの公開**
Docker Composeの`docker-compose.yml`ファイルに、クラスタバスポートを明示的に公開する設定を追加します。

#### **修正例: `docker-compose.yml`**
```yaml
version: '3.9'
services:
  redis-node1:
    image: redis:7
    command: ["redis-server", "--port", "6379", "--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf", "--cluster-node-timeout", "5000", "--appendonly", "yes", "--cluster-announce-ip", "192.168.0.150", "--cluster-announce-port", "6379", "--cluster-announce-bus-port", "16379"]
    ports:
      - "6379:6379"
      - "16379:16379" # クラスタバスポートを公開
    volumes:
      - redis-node1-data:/data

  redis-node2:
    image: redis:7
    command: ["redis-server", "--port", "6380", "--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf", "--cluster-node-timeout", "5000", "--appendonly", "yes", "--cluster-announce-ip", "192.168.0.150", "--cluster-announce-port", "6380", "--cluster-announce-bus-port", "16380"]
    ports:
      - "6380:6380"
      - "16380:16380" # クラスタバスポートを公開
    volumes:
      - redis-node2-data:/data

  redis-node3:
    image: redis:7
    command: ["redis-server", "--port", "6381", "--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf", "--cluster-node-timeout", "5000", "--appendonly", "yes", "--cluster-announce-ip", "192.168.0.150", "--cluster-announce-port", "6381", "--cluster-announce-bus-port", "16381"]
    ports:
      - "6381:6381"
      - "16381:16381" # クラスタバスポートを公開
    volumes:
      - redis-node3-data:/data

volumes:
  redis-node1-data:
  redis-node2-data:
  redis-node3-data:
```

---

### **2.2. Docker Composeの再起動**
修正した設定を適用するため、Docker Composeを再起動します。

```bash
docker-compose down
docker-compose up -d
```

---

### **2.3. クラスタ作成前のリセット**
Redisノードの状態をリセットしてからクラスタを再作成します。

#### **リセット手順**
各ノードで以下を実行して、クラスタ状態をリセットします。
```bash
docker exec -it poc_redis-node1_1 redis-cli -p 6379 cluster reset hard
docker exec -it poc_redis-node2_1 redis-cli -p 6380 cluster reset hard
docker exec -it poc_redis-node3_1 redis-cli -p 6381 cluster reset hard
```

---

### **2.4. クラスタ作成の再試行**
リセット後にクラスタ作成コマンドを再実行します。

```bash
docker exec -it poc_redis-node1_1 redis-cli --cluster create \
192.168.0.150:6379 192.168.0.150:6380 192.168.0.150:6381 \
--cluster-replicas 0
```

---

## **3. 確認作業**

### **3.1. ポートのリッスン確認**
各ノードでクラスタバスポートが開いているか確認します。

```bash
docker exec -it poc_redis-node1_1 netstat -tuln
docker exec -it poc_redis-node2_1 netstat -tuln
docker exec -it poc_redis-node3_1 netstat -tuln
```

- **期待される結果**:
  クラスタバスポート（例: 16379, 16380, 16381）がリッスン状態になっている。

---

### **3.2. クラスタ状態確認**
クラスタ作成後、各ノードでクラスタ状態を確認します。

```bash
docker exec -it poc_redis-node1_1 redis-cli -p 6379 cluster nodes
docker exec -it poc_redis-node1_1 redis-cli -p 6379 cluster info
```

- **期待される結果**:
  - `cluster_state:ok` が表示される。
  - すべてのノードが正しく参加している。

---

## **4. それでも解決しない場合**
- **Dockerネットワークの問題**:
  - Redisノード間のネットワークが切断されていないか確認します。
- **Redisログの確認**:
  - 各ノードのログを確認してエラーがないか調査します：
    ```bash
    docker logs poc_redis-node1_1
    docker logs poc_redis-node2_1
    docker logs poc_redis-node3_1
    ```

---

これらの手順で問題を解決し、Redis Clusterが正常に構成されることを確認してください！


[Docker ComposeとRedisクラスタ4.0の新機能「port-forwarding」を使いRedisクラスタを作成する方法（どんなサイズにも対応可）](https://qiita.com/Reddie_Japan/items/75d26bfc0dfaeab6a5c3)

docker-compose.yaml
```
version: '3.9'
services:
  redis-node1:
    image: redis:7
    command: ["redis-server", "--port", "6379", "--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf", "--cluster-node-timeout", "5000", "--appendonly", "yes", "--cluster-announce-ip", "192.168.0.150", "--cluster-announce-port", "6379", "--cluster-announce-bus-port 16379"]
    ports:
      - "6379:6379"
      - "16379:16379"
    volumes:
      - redis-node1-data:/data

  redis-node2:
    image: redis:7
    command: ["redis-server", "--port", "6380", "--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf", "--cluster-node-timeout", "5000", "--appendonly", "yes", "--cluster-announce-ip", "192.168.0.150", "--cluster-announce-port", "6380", "--cluster-announce-bus-port 16380"]
    ports:
      - "6380:6380"
      - "16380:16380"
    volumes:
      - redis-node2-data:/data

  redis-node3:
    image: redis:7
    command: ["redis-server", "--port", "6381", "--cluster-enabled", "yes", "--cluster-config-file", "nodes.conf", "--cluster-node-timeout", "5000", "--appendonly", "yes", "--cluster-announce-ip", "192.168.0.150", "--cluster-announce-port", "6381", "--cluster-announce-bus-port 16381"]
    ports:
      - "6381:6381"
      - "16381:16381"
    volumes:
      - redis-node3-data:/data

volumes:
  redis-node1-data:
  redis-node2-data:
  redis-node3-data:



```


```
sudo iptables -t nat -nL
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination         
DOCKER     all  --  0.0.0.0/0            0.0.0.0/0            ADDRTYPE match dst-type LOCAL

Chain INPUT (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination         
DOCKER     all  --  0.0.0.0/0           !127.0.0.0/8          ADDRTYPE match dst-type LOCAL

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination         
MASQUERADE  all  --  172.25.0.0/16        0.0.0.0/0           
MASQUERADE  all  --  172.17.0.0/16        0.0.0.0/0           
MASQUERADE  all  --  192.168.49.0/24      0.0.0.0/0           
MASQUERADE  all  --  172.19.0.0/16        0.0.0.0/0           
MASQUERADE  all  --  172.18.0.0/16        0.0.0.0/0           
MASQUERADE  all  --  172.20.0.0/16        0.0.0.0/0           
MASQUERADE  tcp  --  172.25.0.2           172.25.0.2           tcp dpt:16379
MASQUERADE  tcp  --  172.25.0.2           172.25.0.2           tcp dpt:6379
MASQUERADE  tcp  --  172.25.0.3           172.25.0.3           tcp dpt:16381
MASQUERADE  tcp  --  172.25.0.3           172.25.0.3           tcp dpt:6381
MASQUERADE  tcp  --  172.25.0.4           172.25.0.4           tcp dpt:16380
MASQUERADE  tcp  --  172.25.0.4           172.25.0.4           tcp dpt:6380

Chain DOCKER (2 references)
target     prot opt source               destination         
RETURN     all  --  0.0.0.0/0            0.0.0.0/0           
RETURN     all  --  0.0.0.0/0            0.0.0.0/0           
RETURN     all  --  0.0.0.0/0            0.0.0.0/0           
RETURN     all  --  0.0.0.0/0            0.0.0.0/0           
RETURN     all  --  0.0.0.0/0            0.0.0.0/0           
RETURN     all  --  0.0.0.0/0            0.0.0.0/0           
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:16379 to:172.25.0.2:16379
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:6379 to:172.25.0.2:6379
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:16381 to:172.25.0.3:16381
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:6381 to:172.25.0.3:6381
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:16380 to:172.25.0.4:16380
DNAT       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:6380 to:172.25.0.4:6380
```
