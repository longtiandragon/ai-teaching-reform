package com.movie.nbspringproduct.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.movie.nbspringproduct.common.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.Date;

/**
 * 图文课程实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("nb_graphic_course")
public class NbGraphicCourse extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    @TableId(type = IdType.ASSIGN_UUID)
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
     * 课程内容
     */
    private String content;
    
    /**
     * 封面图片
     */
    private String image;
    
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
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
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


