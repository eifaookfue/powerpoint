範囲検索を行えるようにする場合は、どのようなURI設計をすればいいでしょうか？

**範囲検索を行う場合の API 設計** について、REST の設計原則に基づいた方法を紹介します。  
基本的には、クエリパラメータを使用して範囲を指定する方法が一般的です。

---

## **1. クエリパラメータを使用する方法（推奨）**
範囲検索には **`min_` / `max_` プレフィックス** を付けてクエリパラメータで指定するのが一般的です。

### **例: 価格の範囲で商品を検索する**
```plaintext
GET /products?price_min=1000&price_max=5000
```
| パラメータ | 説明 |
|-----------|------|
| `price_min` | 最小価格（1000円以上） |
| `price_max` | 最大価格（5000円以下） |

### **例: 日付の範囲で注文を検索する**
```plaintext
GET /orders?date_from=2024-01-01&date_to=2024-01-31
```
| パラメータ | 説明 |
|-----------|------|
| `date_from` | 検索する開始日（2024-01-01 以降） |
| `date_to` | 検索する終了日（2024-01-31 以前） |

**この方法のメリット**
- シンプルで直感的
- クライアントが片方の条件だけ指定することも可能
  - 例: `GET /products?price_min=1000`（1000円以上の商品を検索）

---

## **2. `range` パラメータを使う方法**
複数の範囲検索をする場合、パラメータ名を整理するために `range` 形式を使うこともあります。

### **例: 価格範囲を `range` で指定**
```plaintext
GET /products?price_range=1000-5000
```

### **例: 日付範囲を `range` で指定**
```plaintext
GET /orders?date_range=2024-01-01,2024-01-31
```

**この方法のメリット**
- URL が短くなり、シンプルに見える
- ただし、クライアント側で `-` や `,` をパースする必要がある

---

## **3. 検索専用のエンドポイントを作成**
もし範囲検索が API の主な用途である場合、検索専用エンドポイントを作成することも考えられます。

```plaintext
GET /products/search?price_min=1000&price_max=5000
GET /orders/search?date_from=2024-01-01&date_to=2024-01-31
```

この方法は、通常の `GET /products` とは区別できるため、  
検索に特化した処理を API 内部で適用しやすいメリットがあります。

---

## **4. GraphQL を使用する場合**
GraphQL では、クエリで範囲を指定するのが一般的です。

```graphql
{
  products(filter: { price: { gte: 1000, lte: 5000 } }) {
    id
    name
    price
  }
}
```
- `gte`（Greater Than or Equal）: 最小値指定 (`>= 1000`)
- `lte`（Less Than or Equal）: 最大値指定 (`<= 5000`)

GraphQL なら `filter` の中に柔軟な検索条件を追加できます。

---

## **まとめ: 最適な URI 設計**
| 方法 | URL 例 | メリット | デメリット |
|------|--------|---------|-----------|
| **✅ クエリパラメータ（推奨）** | `GET /products?price_min=1000&price_max=5000` | シンプルで直感的 | なし |
| **🔹 range 方式** | `GET /products?price_range=1000-5000` | URL が短くなる | クライアントでパースが必要 |
| **🔹 検索専用エンドポイント** | `GET /products/search?price_min=1000&price_max=5000` | 検索専用であることが明確 | API の数が増える |
| **✅ GraphQL** | `products(filter: { price: { gte: 1000, lte: 5000 } })` | 柔軟な検索が可能 | GraphQL 導入が必要 |

---

### **結論（おすすめの設計）**
- **シンプルな範囲検索** → `GET /products?price_min=1000&price_max=5000`
- **複数の範囲検索をスリムにしたい** → `GET /products?price_range=1000-5000`
- **検索専用の API を分けたい** → `GET /products/search?price_min=1000&price_max=5000`
- **GraphQL を使う場合** → `products(filter: { price: { gte: 1000, lte: 5000 } })`

---

REST API なら **クエリパラメータ（`_min` / `_max` 方式）** を使うのが一番分かりやすくておすすめです！ 🚀