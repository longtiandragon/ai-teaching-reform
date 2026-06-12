package com.movie.nbspringproduct.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
public class FileUploadConfig implements WebMvcConfigurer {

    @Value("${file.upload.path:./uploads}")
    private String uploadPath;

    @Value("${file.access.prefix:/uploads}")
    private String accessPrefix;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path uploadRoot = resolveUploadRoot();
        registry.addResourceHandler(accessPrefix + "/**")
                .addResourceLocations(uploadRoot.toUri().toString());
    }

    private Path resolveUploadRoot() {
        Path configuredPath = Paths.get(uploadPath);
        if (configuredPath.isAbsolute()) {
            return configuredPath.normalize();
        }
        return Paths.get(System.getProperty("user.dir")).resolve(configuredPath).normalize();
    }
}
