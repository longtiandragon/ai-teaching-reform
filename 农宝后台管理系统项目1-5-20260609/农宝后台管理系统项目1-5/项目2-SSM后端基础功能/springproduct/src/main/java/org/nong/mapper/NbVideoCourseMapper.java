package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbVideoCourse;

import java.util.List;
import java.util.Map;

/**
 * 视频课程Mapper接口
 */
public interface NbVideoCourseMapper {
    
    /**
     * 查询视频课程列表
     */
    List<NbVideoCourse> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbVideoCourse selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbVideoCourse course);
    
    /**
     * 修改
     */
    int update(NbVideoCourse course);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

