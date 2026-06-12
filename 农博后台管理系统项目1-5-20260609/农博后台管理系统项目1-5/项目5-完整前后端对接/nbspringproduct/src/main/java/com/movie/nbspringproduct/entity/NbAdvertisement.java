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
 * 广告实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("nb_advertisement")
public class NbAdvertisement extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    @TableId(type = IdType.ASSIGN_UUID)
    private String id;
    
    /**
     * 广告标题
     */
    private String title;
    
    /**
     * 广告图片
     */
    private String image;
    
    /**
     * 广告位置（banner首页轮播图/sidebar侧边栏/popup弹窗/footer底部）
     */
    private String position;
    
    /**
     * 链接地址
     */
    private String linkUrl;
    
    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date startTime;
    
    /**
     * 结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date endTime;
    
    /**
     * 排序
     */
    private Integer sort;
    
    /**
     * 状态（0未发布 1已发布）
     */
    private Integer status;
    
    /**
     * 点击量
     */
    private Integer clickCount;
}

