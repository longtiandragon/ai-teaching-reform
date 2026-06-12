package com.movie.nbspringproduct.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.movie.nbspringproduct.common.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.util.Date;

/**
 * 农产品实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("nb_farm_produce")
public class NbFarmProduce extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    @TableId(type = IdType.ASSIGN_UUID)
    private String id;
    
    /**
     * 标题
     */
    private String title;
    
    /**
     * 摘要
     */
    private String resume;
    
    /**
     * 描述
     */
    private String description;
    
    /**
     * 图片
     */
    private String image;
    
    /**
     * 分类
     */
    private String catgory;
    
    /**
     * 产品类型
     */
    private String produceType;
    
    /**
     * 价格
     */
    private BigDecimal price;
    
    /**
     * 浏览数
     */
    private Integer browseNum;
    
    /**
     * 推送状态（0未推送 1已推送）
     */
    private Integer pushStatus;
    
    /**
     * 推送时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date pushTime;
    
    /**
     * 推荐状态（0不推荐 1推荐）
     */
    private Integer recommend;
    
    /**
     * 供应商名称
     */
    private String providerName;
    
    /**
     * 账户ID
     */
    private String accountId;
    
    /**
     * 创建时间（字符串格式）
     */
    private String createdTime;
    
    /**
     * 更新时间（字符串格式）
     */
    private String updatedTime;
}

