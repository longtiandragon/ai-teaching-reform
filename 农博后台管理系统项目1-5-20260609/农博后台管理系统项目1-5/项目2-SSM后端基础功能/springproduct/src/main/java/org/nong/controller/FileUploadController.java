package org.nong.controller;

import org.nong.common.Result;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping({"/api/upload", "/api/yjnb/upload"})
public class FileUploadController {

    @Value("${file.upload.path:./uploads}")
    private String uploadPath;

    @Value("${file.access.prefix:/uploads}")
    private String accessPrefix;

    @PostMapping("/image")
    public Result<Map<String, String>> uploadImage(@RequestParam("file") MultipartFile file) {
        if (file == null || file.isEmpty()) {
            return Result.error("Please select a file to upload");
        }

        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            return Result.error("Only image files are allowed");
        }

        return saveFile(file);
    }

    @PostMapping("/file")
    public Result<Map<String, String>> uploadFile(@RequestParam("file") MultipartFile file) {
        if (file == null || file.isEmpty()) {
            return Result.error("Please select a file to upload");
        }

        String contentType = file.getContentType();
        if (contentType == null || (!contentType.startsWith("image/") && !contentType.startsWith("video/"))) {
            return Result.error("Only image or video files are allowed");
        }

        return saveFile(file);
    }

    @PostMapping("/images")
    public Result<Map<String, Object>> uploadImages(@RequestParam("files") MultipartFile[] files) {
        if (files == null || files.length == 0) {
            return Result.error("Please select files to upload");
        }

        Map<String, Object> data = new HashMap<>();
        data.put("total", files.length);
        data.put("success", 0);
        data.put("failed", 0);

        for (MultipartFile file : files) {
            Result<Map<String, String>> result = uploadImage(file);
            if (result.getCode() == 200) {
                data.put("success", (Integer) data.get("success") + 1);
            } else {
                data.put("failed", (Integer) data.get("failed") + 1);
            }
        }

        return Result.success(data);
    }

    private Result<Map<String, String>> saveFile(MultipartFile file) {
        try {
            String originalFilename = file.getOriginalFilename();
            if (originalFilename == null || !originalFilename.contains(".")) {
                return Result.error("Filename is empty");
            }

            String extension = originalFilename.substring(originalFilename.lastIndexOf(".")).toLowerCase();
            String datePath = new SimpleDateFormat("yyyy/MM/dd").format(new Date());
            String fileName = UUID.randomUUID().toString().replace("-", "") + extension;

            File dir = resolveUploadRoot().resolve(datePath).toFile();
            if (!dir.exists() && !dir.mkdirs()) {
                return Result.error("Failed to create upload directory: " + dir.getAbsolutePath());
            }

            File dest = dir.toPath().resolve(fileName).toFile();
            file.transferTo(dest);

            String fileUrl = accessPrefix + "/" + datePath + "/" + fileName;
            Map<String, String> data = new HashMap<>();
            data.put("url", fileUrl);
            data.put("fileName", originalFilename);
            data.put("fileSize", String.valueOf(file.getSize()));
            return Result.success(data);
        } catch (IOException e) {
            return Result.error("File upload failed: " + e.getMessage());
        }
    }

    private Path resolveUploadRoot() {
        Path configuredPath = Paths.get(uploadPath);
        if (configuredPath.isAbsolute()) {
            return configuredPath.normalize();
        }
        return Paths.get(System.getProperty("user.dir")).resolve(configuredPath).normalize();
    }
}
