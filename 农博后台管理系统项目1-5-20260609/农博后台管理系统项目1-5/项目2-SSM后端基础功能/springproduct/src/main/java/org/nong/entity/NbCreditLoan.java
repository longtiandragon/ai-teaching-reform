package org.nong.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.nong.common.BaseEntity;

import java.util.Date;

/**
 * 信贷信息实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class NbCreditLoan extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    private String id;
    
    /**
     * 标题
     */
    private String title;
    
    /**
     * 作者
     */
    private String author;
    
    /**
     * 摘要
     */
    private String resume;
    
    /**
     * 内容
     */
    private String content;
    
    /**
     * 图片
     */
    private String image;
    
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

