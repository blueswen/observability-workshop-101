package com.example.app;

import io.prometheus.client.exemplars.tracer.otel_agent.OpenTelemetryAgentSpanContextSupplier;
import org.springframework.context.annotation.*;
import org.springframework.core.type.AnnotatedTypeMetadata;

@Configuration
public class PrometheusExemplarSamplerConfiguration {

    @Bean
    @Conditional(OnOpenTelemetryAgentPresentCondition.class)
    public OpenTelemetryAgentSpanContextSupplier openTelemetryAgentSpanContextSupplier() {
        return new OpenTelemetryAgentSpanContextSupplier();
    }

    static class OnOpenTelemetryAgentPresentCondition implements Condition {

        @Override
        public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
            try {
                // This checks if the OpenTelemetry agent's shaded Span class is present on the classpath
                Class.forName("io.opentelemetry.javaagent.shaded.io.opentelemetry.api.trace.Span");
                return true;
            } catch (ClassNotFoundException e) {
                // The OpenTelemetry agent's shaded Span class is not present
                return false;
            }
        }
    }
}
