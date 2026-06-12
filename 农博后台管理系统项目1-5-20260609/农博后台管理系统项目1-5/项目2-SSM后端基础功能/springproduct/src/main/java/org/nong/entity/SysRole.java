package org.nong.entity;

import lombok.Data;

import java.io.Serializable;

/**
 * 角色实体类
 */
@Data
public class SysRole implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    /**
     * 角色ID
     */
    private String id;
    
    /**
     * 角色名称
     */
    private String roleName;
    
    /**
     * 角色权限字符串
     */
    private String roleKey;
    
    /**
     * 显示顺序
     */
    private Integer roleSort;
    
    /**
     * 数据范围（1：全部数据权限 2：自定数据权限 3：本部门数据权限 4：本部门及以下数据权限）
     */
    private Integer dataScope;
    
    /**
     * 角色状态（0正常 1停用）
     */
    private Integer status;
    
    /**
     * 删除标志（0代表存在 1代表删除）
     */
    private Integer delFlag;
    
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

