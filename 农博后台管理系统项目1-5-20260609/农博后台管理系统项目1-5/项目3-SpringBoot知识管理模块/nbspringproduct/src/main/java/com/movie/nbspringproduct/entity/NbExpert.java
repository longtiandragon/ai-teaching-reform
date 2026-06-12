package com.movie.nbspringproduct.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.movie.nbspringproduct.common.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 专家实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("nb_expert")
public class NbExpert extends BaseEntity {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 主键ID
     */
    @TableId(type = IdType.ASSIGN_UUID)
    private String id;
    
    /**
     * 专家姓名
     */
    private String name;
    
    /**
     * 专家头像
     */
    private String avatar;
    
    /**
     * 专业领域
     */
    private String specialty;
    
    /**
     * 职称
     */
    private String title;
    
    /**
     * 所属机构
     */
    private String organization;
    
    /**
     * 联系电话
     */
    private String phone;
    
    /**
     * 电子邮箱
     */
    private String email;
    
    /**
     * 个人简介
     */
    private String introduction;
    
    /**
     * 服务次数
     */
    private Integer serviceCount;
    
    /**
     * 评分
     */
    private String rating;
    
    /**
     * 状态（0不可用 1可用）
     */
    private Integer status;
}

