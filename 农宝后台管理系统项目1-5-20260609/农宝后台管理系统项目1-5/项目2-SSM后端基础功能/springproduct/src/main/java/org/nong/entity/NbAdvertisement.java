package org.nong.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.nong.common.BaseEntity;

import java.util.Date;

/**
 * 广告实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class NbAdvertisement extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
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
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date startTime;
    
    /**
     * 结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
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

