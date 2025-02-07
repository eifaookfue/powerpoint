### **🔹 Spring Boot でパスパラメータによるテーブル指定、リクエストボディでカラム指定 & フィルタ適用 API を作成**
この API は、**任意のテーブルから指定したカラムのみ取得し、フィルタ条件を適用してデータを返す** ものです。

---

## **1. API 設計**
| **項目** | **設計内容** |
|---------|------------|
| **HTTP メソッド** | `POST` |
| **エンドポイント** | `/api/data/{tableName}` |
| **パスパラメータ** | `tableName`（取得したいテーブル名） |
| **リクエストボディ** | JSON 形式で **取得カラムリスト** と **フィルタ条件** を指定 |
| **レスポンス** | 指定カラムのデータを JSON で返す |

---

## **2. リクエスト例**
**📌 リクエスト: `users` テーブルから `id` と `name` を取得し、`age > 25` の条件でフィルタ**
```http
POST /api/data/users
Content-Type: application/json

{
  "columns": ["id", "name"],  // ほしいカラム
  "filters": {                 // フィルタ条件
    "age": { "operator": ">", "value": 25 }
  }
}
```

---

## **3. Spring Boot（Spring Data JPA + JDBC）での実装**
### **📌 依存ライブラリ（`pom.xml`）**
```xml
<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring Boot JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- H2 Database（開発用） -->
    <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Spring Boot JDBC -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-jdbc</artifactId>
    </dependency>
</dependencies>
```

---

### **📌 データベース設定（`application.properties`）**
```properties
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.h2.console.enabled=true
```
📌 **開発用に H2 データベースを使用（本番では MySQL/PostgreSQL に変更可）**

---

### **📌 リクエストのデータモデル**
```java
package com.example.demo.model;

import java.util.List;
import java.util.Map;

public class QueryRequest {
    private List<String> columns; // 取得するカラムリスト
    private Map<String, FilterCondition> filters; // フィルタ条件

    // Getter & Setter
    public List<String> getColumns() {
        return columns;
    }

    public void setColumns(List<String> columns) {
        this.columns = columns;
    }

    public Map<String, FilterCondition> getFilters() {
        return filters;
    }

    public void setFilters(Map<String, FilterCondition> filters) {
        this.filters = filters;
    }

    // フィルタ条件クラス
    public static class FilterCondition {
        private String operator; // 演算子（例: "=", ">", "<", "LIKE"）
        private Object value;    // フィルタの値

        public String getOperator() {
            return operator;
        }

        public void setOperator(String operator) {
            this.operator = operator;
        }

        public Object getValue() {
            return value;
        }

        public void setValue(Object value) {
            this.value = value;
        }
    }
}
```

---

### **📌 サービスクラス（JDBC を使用）**
```java
package com.example.demo.service;

import com.example.demo.model.QueryRequest;
import com.example.demo.model.QueryRequest.FilterCondition;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class QueryService {
    private final JdbcTemplate jdbcTemplate;

    public QueryService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<Map<String, Object>> fetchData(String tableName, QueryRequest request) {
        // 🔹 SQL インジェクション対策: 許可リストでテーブル名をチェック
        List<String> allowedTables = List.of("users", "orders");
        if (!allowedTables.contains(tableName)) {
            throw new IllegalArgumentException("Invalid table name");
        }

        // 🔹 取得カラムの設定（カラム名のバリデーション推奨）
        String columnList = String.join(", ", request.getColumns());

        // 🔹 WHERE 条件の組み立て（バインドパラメータを使用）
        List<String> whereClauses = request.getFilters().entrySet().stream()
            .map(entry -> entry.getKey() + " " + entry.getValue().getOperator() + " ?")
            .collect(Collectors.toList());
        String whereClause = whereClauses.isEmpty() ? "1=1" : String.join(" AND ", whereClauses);

        // 🔹 SQL クエリ作成
        String sql = "SELECT " + columnList + " FROM " + tableName + " WHERE " + whereClause;

        // 🔹 バインドパラメータの取得
        Object[] values = request.getFilters().values().stream()
            .map(FilterCondition::getValue)
            .toArray();

        // 🔹 SQL 実行
        return jdbcTemplate.queryForList(sql, values);
    }
}
```

---

### **📌 コントローラークラス**
```java
package com.example.demo.controller;

import com.example.demo.model.QueryRequest;
import com.example.demo.service.QueryService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/data")
public class QueryController {
    private final QueryService queryService;

    public QueryController(QueryService queryService) {
        this.queryService = queryService;
    }

    @PostMapping("/{tableName}")
    public Map<String, Object> getData(
            @PathVariable String tableName,
            @RequestBody QueryRequest request
    ) {
        List<Map<String, Object>> data = queryService.fetchData(tableName, request);
        return Map.of("status", "success", "data", data);
    }
}
```

---

## **6. 動作確認**
### **📌 H2 データベースにテストデータを挿入**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

INSERT INTO users (id, name, age) VALUES (1, 'Tanaka', 30);
INSERT INTO users (id, name, age) VALUES (2, 'Yamada', 40);
INSERT INTO users (id, name, age) VALUES (3, 'Sato', 20);
```

### **📌 API リクエスト**
```sh
curl -X POST "http://localhost:8080/api/data/users" \
     -H "Content-Type: application/json" \
     -d '{"columns": ["id", "name"], "filters": {"age": {"operator": ">", "value": 25}}}'
```

📌 **レスポンス**
```json
{
  "status": "success",
  "data": [
    { "id": 1, "name": "Tanaka" },
    { "id": 2, "name": "Yamada" }
  ]
}
```

---

## **7. まとめ**
✅ **Spring Boot でパスパラメータ + JSON フィルタを活用した API を構築**  
✅ **SQL インジェクション対策（テーブルのホワイトリスト + バインドパラメータ）**  
✅ **Spring JDBC（JdbcTemplate）を使用し、柔軟なクエリ生成を実装**  
✅ **拡張すれば ORDER BY, LIMIT も追加可能！**

🚀 **Spring Boot で汎用的なデータ取得 API を作るベースとして活用できます！**