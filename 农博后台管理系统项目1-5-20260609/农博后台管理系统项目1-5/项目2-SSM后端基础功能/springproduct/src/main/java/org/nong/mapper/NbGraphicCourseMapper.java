package org.nong.mapper;

import org.apache.ibatis.annotations.Param;
import org.nong.entity.NbGraphicCourse;

import java.util.List;
import java.util.Map;

/**
 * 图文课程Mapper接口
 */
public interface NbGraphicCourseMapper {
    
    /**
     * 查询图文课程列表
     */
    List<NbGraphicCourse> selectList(Map<String, Object> params);
    
    /**
     * 查询总数
     */
    Long selectCount(Map<String, Object> params);
    
    /**
     * 根据ID查询
     */
    NbGraphicCourse selectById(@Param("id") String id);
    
    /**
     * 新增
     */
    int insert(NbGraphicCourse course);
    
    /**
     * 修改
     */
    int update(NbGraphicCourse course);
    
    /**
     * 删除
     */
    int deleteById(@Param("id") String id);
    
    /**
     * 批量删除
     */
    int deleteBatch(@Param("ids") String[] ids);
}

