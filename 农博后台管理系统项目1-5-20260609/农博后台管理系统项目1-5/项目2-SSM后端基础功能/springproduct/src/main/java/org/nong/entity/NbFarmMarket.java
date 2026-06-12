package org.nong.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;
import org.nong.common.BaseEntity;

/**
 * 农贸市场实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class NbFarmMarket extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    private Integer id;
    
    /**
     * 市场名称
     */
    private String name;
    
    /**
     * 区域ID
     */
    private String regionId;
    
    /**
     * 创建时间（字符串格式）
     */
    private String createdTime;
    
    /**
     * 更新时间（字符串格式）
     */
    private String updatedTime;
}

