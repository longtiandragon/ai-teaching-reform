package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbGraphicCourse;

import java.util.Map;

/**
 * 图文课程Service接口
 */
public interface INbGraphicCourseService {
    
    Result<NbGraphicCourse> selectList(Map<String, Object> params);
    
    NbGraphicCourse selectById(String id);
    
    int insert(NbGraphicCourse course);
    
    int update(NbGraphicCourse course);
    
    int deleteById(String id);
    
    int deleteBatch(String[] ids);
}

