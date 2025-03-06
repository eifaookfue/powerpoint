RedisとCaffeineとSpringBootを使ってローカルキャッシュを活用にするにはどうしたらいいですか？

### **Spring Boot + Redis + Caffeine を活用してローカルキャッシュを最適化する方法**
Spring Boot では、**Caffeine（ローカルキャッシュ）** と **Redis（分散キャッシュ）** を組み合わせて、**効率的なキャッシュ戦略** を構築できます。

---

## **1. Redis & Caffeine の組み合わせのメリット**
| **キャッシュ** | **特性** | **メリット** |
|--------------|--------|------------|
| **Caffeine（ローカルキャッシュ）** | メモリ内の高速キャッシュ | **超高速**（ミリ秒以下） |
| **Redis（分散キャッシュ）** | ネットワーク上のキャッシュ | **複数ノードで共有可能** |

✅ **データ取得の優先順位**
1. **Caffeine（ローカルキャッシュ）を先にチェック**（最速）
2. **Caffeine にデータがない場合、Redis から取得**
3. **Redis にもデータがない場合、DB から取得し、両方のキャッシュに保存**

---

## **2. Spring Boot で Redis + Caffeine を設定**
### **(1) 依存関係を追加**
`pom.xml` に以下を追加：
```xml
<dependencies>
    <!-- Spring Boot Cache -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-cache</artifactId>
    </dependency>

    <!-- Caffeine（ローカルキャッシュ） -->
    <dependency>
        <groupId>com.github.ben-manes.caffeine</groupId>
        <artifactId>caffeine</artifactId>
        <version>3.1.6</version>
    </dependency>

    <!-- Redis（分散キャッシュ） -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
</dependencies>
```

---

### **(2) キャッシュ設定（`CacheConfig.java`）**
**Redis + Caffeine を組み合わせるために `CompositeCacheManager` を設定**：
```java
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.cache.support.CompositeCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.connection.RedisConnectionFactory;

import java.time.Duration;
import java.util.Arrays;

@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        return new LettuceConnectionFactory("localhost", 6379);
    }

    @Bean
    public CacheManager cacheManager(RedisConnectionFactory redisConnectionFactory) {
        // Caffeine（ローカルキャッシュ）の設定
        CaffeineCacheManager caffeineCacheManager = new CaffeineCacheManager();
        caffeineCacheManager.setCaffeine(com.github.benmanes.caffeine.Caffeine.newBuilder()
                .maximumSize(1000) // 最大 1000 件キャッシュ
                .expireAfterWrite(Duration.ofMinutes(10)) // 10分後にキャッシュ削除
        );

        // Redis（分散キャッシュ）の設定
        RedisCacheConfiguration redisCacheConfig = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofHours(1)); // 1時間のTTL

        RedisCacheManager redisCacheManager = RedisCacheManager.builder(redisConnectionFactory)
                .cacheDefaults(redisCacheConfig)
                .build();

        // Caffeine + Redis のハイブリッドキャッシュ
        CompositeCacheManager compositeCacheManager = new CompositeCacheManager(caffeineCacheManager, redisCacheManager);
        compositeCacheManager.setFallbackToNoOpCache(true); // どちらのキャッシュも見つからない場合、キャッシュなし
        return compositeCacheManager;
    }
}
```
**この設定で：**
1. **Caffeine でローカルキャッシュ**
2. **Caffeine にない場合、Redis から取得**
3. **Redis にない場合、データを DB から取得してキャッシュ**

---

### **(3) キャッシュを使用する**
Spring の `@Cacheable` アノテーションを使ってキャッシュを適用。
```java
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class EmployeeService {

    @Cacheable(value = "employeeCache", key = "#id")
    public Employee getEmployeeById(Long id) {
        // DB からデータを取得（実際のデータベース処理を模擬）
        return fetchEmployeeFromDatabase(id);
    }

    private Employee fetchEmployeeFromDatabase(Long id) {
        System.out.println("Fetching from DB...");
        return new Employee(id, "John Doe", "Engineering");
    }
}
```
---
### **(4) キャッシュの確認**
キャッシュが正しく機能しているか確認。

```sh
# 初回取得（DB からデータ取得）
curl http://localhost:8080/employee/1
# => "Fetching from DB..." がログに表示

# 2回目以降（キャッシュから取得）
curl http://localhost:8080/employee/1
# => DBアクセスなし（高速取得）
```

---

## **3. キャッシュの手動操作**
### **キャッシュのクリア**
キャッシュを削除するには `@CacheEvict` を使う。

```java
@CacheEvict(value = "employeeCache", key = "#id")
public void evictEmployeeCache(Long id) {
    System.out.println("Cache evicted for employee ID: " + id);
}
```
```sh
curl -X DELETE http://localhost:8080/employee/1
```
---
### **キャッシュの更新**
キャッシュの値を更新するには `@CachePut` を使用。

```java
@CachePut(value = "employeeCache", key = "#employee.id")
public Employee updateEmployee(Employee employee) {
    System.out.println("Updating employee in DB...");
    return employee;
}
```
```sh
curl -X PUT -H "Content-Type: application/json" -d '{"id":1, "name":"Alice"}' http://localhost:8080/employee
```
---

## **4. まとめ**
| **機能** | **Caffeine（ローカルキャッシュ）** | **Redis（分散キャッシュ）** |
|---------|------------------|----------------|
| **アクセス速度** | **ナノ秒レベル（超高速）** | **ミリ秒レベル（ネットワーク通信）** |
| **キャッシュのスコープ** | **1つのアプリケーション内** | **クラスタ全体で共有** |
| **データ永続性** | **アプリ終了時に消える** | **再起動後も保持可能** |
| **TTL（有効期限）** | **短い（メモリ節約のため）** | **長めに設定可能** |

💡 **オススメのキャッシュ戦略**
1. **最も高速なアクセスが必要なデータは** → **Caffeine（ローカルキャッシュ）**
2. **複数のノードで共有するデータは** → **Redis（分散キャッシュ）**
3. **Caffeine でキャッシュしつつ、Redis も活用するハイブリッド構成が最適！** 🚀