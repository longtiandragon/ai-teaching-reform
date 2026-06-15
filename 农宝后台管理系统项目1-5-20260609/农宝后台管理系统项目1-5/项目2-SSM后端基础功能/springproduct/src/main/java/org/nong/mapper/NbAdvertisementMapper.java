package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbAdvertisement;

import java.util.List;
import java.util.Map;

/**
 * 广告Mapper接口
 */
public interface NbAdvertisementMapper {
    
    /**
     * 查询广告列表
     */
    List<NbAdvertisement> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbAdvertisement selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbAdvertisement ad);
    
    /**
     * 修改
     */
    int update(NbAdvertisement ad);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

