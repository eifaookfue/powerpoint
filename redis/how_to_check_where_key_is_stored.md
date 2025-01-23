redis-cliで各ノードにデータがどれくらい保存されているか確認することはできますか？

はい、`redis-cli`を使用して各Redisノードに保存されているデータ量を確認できます。以下の方法で確認可能です。

---

## **1. Redisのデータ量を確認する方法**

### **1.1. `DBSIZE`コマンド**
`DBSIZE`コマンドを使うと、現在のRedisデータベース（デフォルト: DB 0）に保存されているキーの総数を確認できます。

#### **コマンド例**
```bash
docker exec -it poc_redis-node1_1 redis-cli -p 6379 dbsize
```

#### **結果例**
```plaintext
(integer) 100
```
- ノード`6379`に100個のキーが保存されていることを示しています。

---

### **1.2. `INFO`コマンド**
`INFO`コマンドを使うと、Redisの詳細な情報（キーの数やメモリ使用量など）を確認できます。

#### **コマンド例**
```bash
docker exec -it poc_redis-node1_1 redis-cli -p 6379 info keyspace
```

#### **結果例**
```plaintext
# Keyspace
db0:keys=100,expires=10,avg_ttl=123456
```
- **`keys`**: キーの総数。
- **`expires`**: 有効期限が設定されているキーの数。
- **`avg_ttl`**: キーの平均TTL（Time to Live: 残り生存時間、ミリ秒）。

---

## **2. クラスタ構成の場合、各スロットのキー数を確認する**

Redis Clusterを使用している場合、各ノードがスロットの一部を担当しているため、特定のスロットに保存されているキーの数を確認できます。

### **2.1. `CLUSTER KEYSLOT`コマンド**
キーがどのスロットに割り当てられているか確認します。

#### **コマンド例**
```bash
docker exec -it poc_redis-node1_1 redis-cli -p 6379 cluster keyslot your-key
```

#### **結果例**
```plaintext
(integer) 12345
```

---

### **2.2. 各スロットに割り当てられたキー数を確認する**
`CLUSTER NODES`と`DBSIZE`を組み合わせて、各ノードのデータ量を確認します。

#### **手順**
1. 各ノードのスロットを確認：
   ```bash
   docker exec -it poc_redis-node1_1 redis-cli -p 6379 cluster nodes
   ```
   これにより、各ノードが管理しているスロットの範囲が表示されます。

2. 各ノードで`DBSIZE`を実行：
   ```bash
   docker exec -it poc_redis-node1_1 redis-cli -p 6379 dbsize
   docker exec -it poc_redis-node2_1 redis-cli -p 6380 dbsize
   docker exec -it poc_redis-node3_1 redis-cli -p 6381 dbsize
   ```

---

## **3. メモリ使用量を確認する**

### **3.1. `INFO memory`コマンド**
各ノードのメモリ使用量を確認します。

#### **コマンド例**
```bash
docker exec -it poc_redis-node1_1 redis-cli -p 6379 info memory
```

#### **結果例**
```plaintext
# Memory
used_memory:1024000
used_memory_human:1000K
used_memory_rss:2048000
used_memory_peak:2048000
used_memory_peak_human:2M
```

- **`used_memory`**: 現在使用しているメモリ量（バイト単位）。
- **`used_memory_human`**: 現在使用しているメモリ量（人間が読みやすい形式）。
- **`used_memory_peak`**: 過去に使用したメモリの最大量。

---

## **4. クラスタ全体のデータ量をまとめて確認**

もし複数ノードのデータ量をまとめて確認したい場合、スクリプトを作成することで効率的に確認できます。

### **スクリプト例（LinuxまたはMac）**
以下のスクリプトを使用して、全ノードの`DBSIZE`を取得できます。

```bash
for port in 6379 6380 6381; do
  echo "Node on port $port:"
  docker exec -it poc_redis-node1_1 redis-cli -p $port dbsize
done
```

---

## **5. まとめ**
- **キーの数**: `DBSIZE`または`INFO keyspace`で確認可能。
- **メモリ使用量**: `INFO memory`で詳細を確認。
- **クラスタ全体の確認**: 各ノードで個別にコマンドを実行するか、スクリプトで自動化。

これで、各Redisノードのデータ量を効率的に確認できます！