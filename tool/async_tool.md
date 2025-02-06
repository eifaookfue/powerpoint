以下は、Springフレームワークを使ってマルチスレッドで同時にAPIリクエストを送信するコード例です。このコードでは、`@Async`を活用して非同期処理を実現します。また、`RestTemplate`を使用してAPIリクエストを送信します。

1. **Maven依存関係**:\
   Spring Bootのプロジェクトを作成し、以下の依存関係を`pom.xml`に追加してください。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-task</artifactId>
</dependency>
```

2. **コード例**

以下に、マルチスレッドでAPIリクエストを送信するためのコードを示します。

### アプリケーションコード

#### `AsyncConfig` (非同期処理の設定)

```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration
@EnableAsync
public class AsyncConfig {

    @Value("${async.corePoolSize:5}")
    private int corePoolSize;

    @Value("${async.maxPoolSize:10}")
    private int maxPoolSize;

    @Value("${async.queueCapacity:50}")
    private int queueCapacity;

    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(corePoolSize); // スレッドプールの最小サイズ
        executor.setMaxPoolSize(maxPoolSize); // スレッドプールの最大サイズ
        executor.setQueueCapacity(queueCapacity); // キューの容量
        executor.setThreadNamePrefix("AsyncThread-");
        executor.initialize();
        return executor;
    }
}
```

#### `AsyncService` (非同期API呼び出し)

```java
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class AsyncService {

    private final RestTemplate restTemplate;

    public AsyncService() {
        this.restTemplate = new RestTemplate();
    }

    @Async
    public void callApi(String url) {
        String response = restTemplate.getForObject(url, String.class);
        System.out.println("Response from " + url + ": " + response);
    }
}
```

#### `MainController` (APIをトリガーするコントローラ)

```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MainController {

    private final AsyncService asyncService;

    public MainController(AsyncService asyncService) {
        this.asyncService = asyncService;
    }

    @GetMapping("/trigger-api")
    public String triggerApi(@RequestParam("url") String url, @RequestParam("count") int count) {
        for (int i = 0; i < count; i++) {
            asyncService.callApi(url);
        }
        return "API calls triggered!";
    }
}
```

3. **application.ymlの設定**

`application.yml`に以下のように非同期設定を記載します：

```yaml
async:
  corePoolSize: 5
  maxPoolSize: 10
  queueCapacity: 50
```

4. **動作確認**

アプリケーションを起動し、以下のようなリクエストを送信します：

```bash
curl "http://localhost:8080/trigger-api?url=https://jsonplaceholder.typicode.com/todos/1&count=5"
```

### 仕組み

1. `@Async`を使用して、`AsyncService`内で非同期に処理を実行します。
2. `ThreadPoolTaskExecutor`を設定して、スレッドプールを管理します。
3. コントローラからリクエストを受けると、指定された数だけAPIリクエストを非同期で実行します。

これにより、マルチスレッドでAPIリクエストを効率的に送信できます。

