package com.hackathon.ipe;

import com.hackathon.ipe.config.AsyncSyncConfiguration;
import com.hackathon.ipe.config.EmbeddedElasticsearch;
import com.hackathon.ipe.config.EmbeddedSQL;
import com.hackathon.ipe.config.JacksonConfiguration;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * Base composite annotation for integration tests.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@SpringBootTest(classes = { IpeApp.class, JacksonConfiguration.class, AsyncSyncConfiguration.class })
@EmbeddedElasticsearch
@EmbeddedSQL
public @interface IntegrationTest {
}
