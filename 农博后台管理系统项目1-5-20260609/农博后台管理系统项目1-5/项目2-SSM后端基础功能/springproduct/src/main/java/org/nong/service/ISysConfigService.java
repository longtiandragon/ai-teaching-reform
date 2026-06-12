package org.nong.service;

import org.nong.entity.SysConfig;
import java.util.List;

public interface ISysConfigService {
    List<SysConfig> selectAll();
    SysConfig selectById(String id);
    SysConfig selectByKey(String configKey);
    int insert(SysConfig config);
    int update(SysConfig config);
    int updateByKey(SysConfig config);
    int batchUpdate(List<SysConfig> configs);
}

