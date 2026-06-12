package org.nong.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.nong.common.BaseEntity;

import java.util.Date;

/**
 * 视频课程实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class NbVideoCourse extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    private String id;
    
    /**
     * 课程标题
     */
    private String title;
    
    /**
     * 讲师姓名
     */
    private String teacher;
    
    /**
     * 课程简介
     */
    private String resume;
    
    /**
     * 课程介绍
     */
    private String content;
    
    /**
     * 封面图片
     */
    private String image;
    
    /**
     * 视频链接
     */
    private String videoUrl;
    
    /**
     * 时长
     */
    private String duration;
    
    /**
     * 课程分类
     */
    private String category;
    
    /**
     * 浏览数
     */
    private Integer browseNum;
    
    /**
     * 发布状态（0未发布 1已发布）
     */
    private Integer publishStatus;
    
    /**
     * 发布时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date publishTime;
    
    /**
     * 推荐状态（0不推荐 1推荐）
     */
    private Integer recommend;
    
    /**
     * 创建时间（字符串格式）
     */
    private String createdTime;
    
    /**
     * 更新时间（字符串格式）
     */
    private String updatedTime;
}

