package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbService;

import java.util.List;
import java.util.Map;

/**
 * 服务Mapper接口
 */
public interface NbServiceMapper {
    
    /**
     * 查询服务列表
     */
    List<NbService> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbService selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbService service);
    
    /**
     * 修改
     */
    int update(NbService service);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

