package com.movie.nbspringproduct.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;

/**
 * 系统配置实体类
 */
@Data
@TableName("sys_config")
public class SysConfig implements Serializable {
    
    /**
     * 配置ID
     */
    @TableId(type = IdType.ASSIGN_UUID)
    private String id;
    
    /**
     * 配置名称
     */
    private String configName;
    
    /**
     * 配置键名
     */
    private String configKey;
    
    /**
     * 配置键值
     */
    private String configValue;
    
    /**
     * 系统内置（Y是 N否）
     */
    private String configType;
    
    /**
     * 备注
     */
    private String remark;
    
    /**
     * 创建时间
     */
    private String createTime;
    
    /**
     * 更新时间
     */
    private String updateTime;
}

