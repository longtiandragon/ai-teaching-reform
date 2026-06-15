package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.SysRole;
import org.nong.mapper.SysRoleMapper;
import org.nong.service.ISysRoleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class SysRoleServiceImpl implements ISysRoleService {
    
    @Autowired
    private SysRoleMapper roleMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<SysRole> selectList(Map<String, Object> params) {
        List<SysRole> list = roleMapper.selectList(params);
        Long total = roleMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public SysRole selectById(String id) {
        return roleMapper.selectById(id);
    }
    
    @Override
    public int insert(SysRole role) {
        if (role.getId() == null || role.getId().isEmpty()) {
            role.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return roleMapper.insert(role);
    }
    
    @Override
    public int update(SysRole role) {
        return roleMapper.update(role);
    }
    
    @Override
    public int deleteById(String id) {
        return roleMapper.deleteById(id);
    }
}

