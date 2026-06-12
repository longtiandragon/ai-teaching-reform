package org.nong.service;

import org.nong.common.Result;
import org.nong.entity.SysRole;
import java.util.Map;

public interface ISysRoleService {
    Result<SysRole> selectList(Map<String, Object> params);
    SysRole selectById(String id);
    int insert(SysRole role);
    int update(SysRole role);
    int deleteById(String id);
}

