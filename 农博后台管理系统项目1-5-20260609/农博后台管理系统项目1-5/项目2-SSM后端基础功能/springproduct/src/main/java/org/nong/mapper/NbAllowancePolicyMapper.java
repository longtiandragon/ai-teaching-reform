package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbAllowancePolicy;

import java.util.List;
import java.util.Map;

/**
 * 补贴政策Mapper接口
 */
public interface NbAllowancePolicyMapper {
    
    /**
     * 查询补贴政策列表
     */
    List<NbAllowancePolicy> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbAllowancePolicy selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbAllowancePolicy policy);
    
    /**
     * 修改
     */
    int update(NbAllowancePolicy policy);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

