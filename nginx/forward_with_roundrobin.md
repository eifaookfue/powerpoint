Spring Bootが複数起動していてラウンドロビンで転送するにはどうしたらいいですか？

Spring Bootが複数起動している環境で、Nginxを使ってリクエストを**ラウンドロビン方式**で転送するには、**ロードバランサの設定**を行います。Nginxはリバースプロキシ機能を使って複数のバックエンド（Spring Bootアプリケーション）にリクエストを分散できます。

以下に具体的な設定例と解説を示します。

---

## **1. 必要な環境の前提**
- 複数のSpring Bootインスタンスが異なるポートで起動している。
  - 例: 
    - `http://127.0.0.1:8081`
    - `http://127.0.0.1:8082`
    - `http://127.0.0.1:8083`
- Nginxがリクエストを受け取り、これらのバックエンドに負荷分散して転送。

---

## **2. Nginxの設定**

### **nginx.conf または サーバーブロック設定ファイルの例**
以下の例では、リクエストを3つのSpring Bootインスタンスにラウンドロビンで分散します。

```nginx
http {
    upstream backend {
        server 127.0.0.1:8081;
        server 127.0.0.1:8082;
        server 127.0.0.1:8083;
    }

    server {
        listen 80;
        server_name example.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## **3. 設定の詳細**

### **a. upstreamディレクティブ**
- **`upstream backend`**:
  - バックエンドサーバーのリストを定義します。
  - `server` ディレクティブで各Spring Bootインスタンスのアドレスとポートを指定。
  - デフォルトではラウンドロビン方式でリクエストを分散します。

### **b. proxy_pass**
- **`proxy_pass http://backend;`**:
  - `upstream` で定義したバックエンドの名前を指定。
  - リクエストがラウンドロビンで複数のSpring Bootインスタンスに転送されます。

### **c. HTTPヘッダーの設定**
以下のヘッダーをバックエンドに渡して、クライアント情報やプロキシの経路を保持します：
- **`Host`**: 元のリクエストのホスト名。
- **`X-Real-IP`**: クライアントの実際のIPアドレス。
- **`X-Forwarded-For`**: プロキシ経由のクライアントIPアドレス。
- **`X-Forwarded-Proto`**: リクエストのプロトコル（HTTPまたはHTTPS）。

---

## **4. 負荷分散方式のカスタマイズ**

Nginxはデフォルトでラウンドロビン方式を使用しますが、他の分散方式も選択可能です。

### **a. ラウンドロビン（デフォルト）**
- 各リクエストを順番にバックエンドに分配。

### **b. 重み付きラウンドロビン**
- 各サーバーに重み（`weight`）を設定し、高性能なサーバーに多くのリクエストを振り分ける。

```nginx
upstream backend {
    server 127.0.0.1:8081 weight=2;
    server 127.0.0.1:8082 weight=1;
    server 127.0.0.1:8083 weight=1;
}
```

### **c. Least Connections**
- リクエストが少ないサーバーを優先して選択。

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;
}
```

### **d. IP Hash**
- クライアントIPアドレスごとに特定のサーバーにリクエストを割り当て。
- セッション情報を保持する必要がある場合に便利。

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;
}
```

---

## **5. HTTPS を使う場合**
HTTPS を使用する場合、SSL証明書を設定します。

### **例: HTTPS 設定**
```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## **6. 設定の適用手順**

### **a. 設定ファイルのテスト**
設定を保存後、構文エラーがないか確認します。
```bash
sudo nginx -t
```

### **b. Nginx の再起動**
エラーがなければNginxを再起動します。
```bash
sudo systemctl restart nginx
```

---

## **7. 追加の考慮点**
- **ヘルスチェック**:
  - バックエンドサーバーが正常に動作しているかを定期的に確認する設定を追加できます。
- **キャッシュ**:
  - 静的リソースをキャッシュすることでバックエンドの負荷を軽減可能。
- **タイムアウト**:
  - バックエンドサーバーが応答しない場合のタイムアウト設定を適切に調整。

---

## **まとめ**

Nginxを使用してSpring Bootインスタンスにラウンドロビンでリクエストを転送するには、`upstream`ディレクティブを使ったリバースプロキシ設定を行います。さらに、負荷分散方式（ラウンドロビン、Least Connections、IP Hashなど）を要件に応じて調整することで、効率的なリクエスト処理が可能になります。

