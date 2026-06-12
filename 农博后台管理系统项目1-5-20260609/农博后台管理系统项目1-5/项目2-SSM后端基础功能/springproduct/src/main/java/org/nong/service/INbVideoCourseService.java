package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.NbVideoCourse;

import java.util.Map;

public interface INbVideoCourseService {
    Result<NbVideoCourse> selectList(Map<String, Object> params);
    NbVideoCourse selectById(String id);
    int insert(NbVideoCourse course);
    int update(NbVideoCourse course);
    int deleteById(String id);
    int deleteBatch(String[] ids);
}

