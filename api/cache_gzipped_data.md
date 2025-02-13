テーブルから取得したデータを圧縮してレスポンスしたいです。その圧縮したデータをキャッシュできますか？

### **🔹 テーブルのデータを圧縮してレスポンスし、圧縮データをキャッシュする方法**
✅ **結論:** **可能！**  
1. **テーブルのデータを取得**  
2. **Gzip 圧縮（または Brotli / Deflate）**  
3. **圧縮データをキャッシュ（Caffeine / Redis など）**  
4. **キャッシュから圧縮データを取得し、そのままレスポンス**  

---

## **1. アプローチ**
### **✅ 圧縮とキャッシュの流れ**
1. **クライアントが API をリクエスト**
2. **キャッシュ（Caffeine / Redis）に圧縮データがあるかチェック**
   - ある → **キャッシュから直接返す**
   - ない → **DB からデータ取得 → Gzip 圧縮 → キャッシュ保存**
3. **圧縮されたデータを `Content-Encoding: gzip` でレスポンス**
4. **次回以降はキャッシュされた圧縮データをそのままレスポンス（DB アクセスなし）**

---

## **2. Spring Boot の実装**
### **✅ 必要な依存関係（`pom.xml`）**
```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

---

### **✅ キャッシュ設定（Caffeine + Redis）**
```java
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import java.time.Duration;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager caffeineCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager("compressedData");
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(100)  // 最大キャッシュエントリ
            .expireAfterWrite(Duration.ofMinutes(10))  // 10分で削除
        );
        return cacheManager;
    }

    @Bean
    public CacheManager redisCacheManager(RedisConnectionFactory redisConnectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10)); // 10分でキャッシュ削除

        return RedisCacheManager.builder(redisConnectionFactory)
            .cacheDefaults(config)
            .build();
    }
}
```
✅ **Caffeine（メモリ内キャッシュ）+ Redis（分散キャッシュ）を併用できる！**

---

### **✅ テーブルのデータ取得 & Gzip 圧縮**
```java
import org.springframework.cache.annotation.Cacheable;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.zip.GZIPOutputStream;

@Service
public class DataService {

    private final JdbcTemplate jdbcTemplate;

    public DataService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Cacheable(value = "compressedData", key = "#tableName")
    public byte[] getCompressedData(String tableName) throws IOException {
        // 1. データを取得
        List<String> data = jdbcTemplate.queryForList("SELECT * FROM " + tableName, String.class);

        // 2. JSON 形式に変換
        String jsonData = String.join(",", data);

        // 3. Gzip 圧縮
        return compressData(jsonData);
    }

    private byte[] compressData(String data) throws IOException {
        ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
        try (GZIPOutputStream gzipStream = new GZIPOutputStream(byteStream)) {
            gzipStream.write(data.getBytes());
        }
        return byteStream.toByteArray();
    }
}
```
📌 **キャッシュのポイント**
- `@Cacheable("compressedData")` で **圧縮データをキャッシュ**
- `key = "#tableName"` → **テーブルごとにキャッシュ**
- **最初のリクエスト時に圧縮し、次回以降はキャッシュから取得**

---

### **✅ API コントローラ**
```java
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.io.IOException;

@RestController
@RequestMapping("/api")
public class DataController {

    private final DataService dataService;

    public DataController(DataService dataService) {
        this.dataService = dataService;
    }

    @GetMapping("/data/{tableName}")
    public ResponseEntity<byte[]> getCompressedData(@PathVariable String tableName) throws IOException {
        byte[] compressedData = dataService.getCompressedData(tableName);

        HttpHeaders headers = new HttpHeaders();
        headers.add(HttpHeaders.CONTENT_ENCODING, "gzip");
        headers.add(HttpHeaders.CONTENT_TYPE, "application/json");

        return ResponseEntity.ok().headers(headers).body(compressedData);
    }
}
```
📌 **API の動作**
- `GET /api/data/users` をリクエストすると…
  - **キャッシュがあればそのまま Gzip 圧縮データを返す**
  - **キャッシュがなければ DB から取得 & 圧縮 & キャッシュ**
- **`Content-Encoding: gzip` をセットし、圧縮データをレスポンス**

---

## **3. 動作確認**
### **📌 API リクエスト**
```sh
curl -H "Accept-Encoding: gzip" -X GET "http://localhost:8080/api/data/users" --output compressed.json.gz
```
📌 **レスポンスヘッダー**
```http
HTTP/1.1 200 OK
Content-Encoding: gzip
Content-Type: application/json
Cache-Control: max-age=600
```

✅ **圧縮データをキャッシュし、次回以降はキャッシュから高速レスポンス！**

---

## **4. まとめ**
✅ **データ取得後に Gzip 圧縮し、そのままキャッシュ（Caffeine / Redis）**  
✅ **キャッシュがあれば、DB アクセスせずに圧縮データをレスポンス**  
✅ **Caffeine（メモリ）+ Redis（分散キャッシュ）の組み合わせが最適**  
✅ **API では `Content-Encoding: gzip` をセットし、クライアントに圧縮データを送信**  

🚀 **この実装で、DB 負荷を減らしながら、高速な圧縮レスポンスを実現可能！** 🔥