package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbExpert;

import java.util.List;
import java.util.Map;

/**
 * 专家Mapper接口
 */
public interface NbExpertMapper {
    
    /**
     * 查询专家列表
     */
    List<NbExpert> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbExpert selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbExpert expert);
    
    /**
     * 修改
     */
    int update(NbExpert expert);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

