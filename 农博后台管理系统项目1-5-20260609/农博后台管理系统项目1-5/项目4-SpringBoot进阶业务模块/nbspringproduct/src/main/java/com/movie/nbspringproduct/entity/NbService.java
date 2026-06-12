package com.movie.nbspringproduct.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.movie.nbspringproduct.common.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;

/**
 * 服务实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("nb_service")
public class NbService extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    @TableId(type = IdType.ASSIGN_UUID)
    private String id;
    
    /**
     * 服务标题
     */
    private String title;
    
    /**
     * 服务图片
     */
    private String image;
    
    /**
     * 服务摘要
     */
    private String resume;
    
    /**
     * 服务内容
     */
    private String content;
    
    /**
     * 服务类别（supply农资供应/machinery农机服务/tech技术指导/logistics物流配送/finance金融服务）
     */
    private String category;
    
    /**
     * 服务商名称
     */
    private String provider;
    
    /**
     * 联系电话
     */
    private String phone;
    
    /**
     * 服务价格
     */
    private BigDecimal price;
    
    /**
     * 状态（0下架 1上架）
     */
    private Integer status;
    
    /**
     * 服务地址
     */
    private String address;
    
    /**
     * 订单数量
     */
    private Integer orderCount;
    
    /**
     * 评分
     */
    private BigDecimal rating;
}

