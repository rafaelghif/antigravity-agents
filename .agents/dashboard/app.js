// AAC V2 Dashboard Client Logic

// Global function to switch tabs
window.switchTab = function(btn, tabId) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  btn.classList.add('active');
  const targetTab = document.getElementById(tabId + '-tab');
  if (targetTab) {
    targetTab.classList.add('active');
  }
};

// Global function to toggle subtask status
window.toggleTask = async function(taskIndex, completed) {
  try {
    const res = await fetch('/api/task/toggle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        taskIndex: taskIndex,
        completed: completed
      })
    });
    if (res.ok) {
      // Reload dashboard data instantly
      window.loadData(false);
    } else {
      console.error('Failed to toggle task status.');
    }
  } catch (err) {
    console.error('Error toggling task:', err);
  }
};

// Global function to load dashboard data
window.loadData = async function(force = false) {
  const refreshBtns = document.querySelectorAll('.btn-action');
  if (force) {
    refreshBtns.forEach(btn => {
      btn.disabled = true;
      btn.textContent = 'Auditing...';
    });
  }

  try {
    const url = force ? '/api/status?force=true' : '/api/status';
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    
    // Manage button states based on server auditing flag
    if (data.auditing) {
      refreshBtns.forEach(btn => {
        btn.disabled = true;
        btn.textContent = 'Auditing...';
      });
    } else {
      refreshBtns.forEach(btn => {
        btn.disabled = false;
        btn.textContent = 'Refresh Audit';
      });
    }
    
    // 1. Version Info
    const versionBadge = document.getElementById('version-badge');
    if (versionBadge) {
      versionBadge.textContent = 'v' + (data.version || '2.109.0');
    }

    // 2. Compliance Audits
    const complianceList = document.getElementById('compliance-list');
    if (complianceList) {
      complianceList.innerHTML = '';
      if (data.compliance) {
        for (const [name, passed] of Object.entries(data.compliance)) {
          const item = document.createElement('div');
          item.className = 'compliance-item';
          item.innerHTML = `
            <span class="name">${name}</span>
            <span class="status-badge ${passed ? 'pass' : 'fail'}">${passed ? 'PASS' : 'FAIL'}</span>
          `;
          complianceList.appendChild(item);
        }
      }
    }
    
    const timestamp = document.getElementById('compliance-timestamp');
    if (timestamp) {
      timestamp.textContent = 'Updated: ' + (data.timestamp || 'Just now');
    }

    // 3. Active Issue Details
    const issue = data.active_issue || { id: "None", title: "No Active Issue Checked Out", status: "closed", tasks: [], branch: "unknown" };
    const issueTitleEl = document.getElementById('active-issue-title');
    if (issueTitleEl) {
      issueTitleEl.textContent = issue.id !== 'None' ? `${issue.id}: ${issue.title}` : issue.title;
    }
    const issueBranchEl = document.getElementById('active-issue-branch');
    if (issueBranchEl) {
      issueBranchEl.textContent = issue.branch || 'unknown';
    }

    // 4. Interactive Tasks
    const activeTasksList = document.getElementById('active-tasks-list');
    if (activeTasksList) {
      activeTasksList.innerHTML = '';
      if (issue.tasks && issue.tasks.length > 0) {
        issue.tasks.forEach((task, idx) => {
          const checked = task.toLowerCase().includes('[x]');
          const cleanLabel = task.replace(/^-\s+\[\s*[xX\s]\s*\]\s*/, '');
          const item = document.createElement('div');
          item.className = 'task-item' + (checked ? ' done' : '');
          item.innerHTML = `
            <div class="task-checkbox"></div>
            <span class="task-label">${cleanLabel}</span>
          `;
          item.addEventListener('click', () => {
            window.toggleTask(idx, !checked);
          });
          activeTasksList.appendChild(item);
        });
      } else {
        activeTasksList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No tasks defined in the active issue file.</p>';
      }
    }

    // 5. Git Status
    const gitStatusList = document.getElementById('git-status-list');
    if (gitStatusList) {
      gitStatusList.innerHTML = '';
      if (data.git_status && data.git_status.length > 0) {
        data.git_status.forEach(file => {
          const isStaged = file.startsWith('M') || file.startsWith('A') || file.startsWith('D') || file.startsWith('R');
          const item = document.createElement('div');
          item.className = 'git-file' + (isStaged ? ' staged' : '');
          item.style.fontFamily = "'Fira Code', monospace";
          item.style.fontSize = "0.8rem";
          item.style.padding = "0.3rem 0.5rem";
          item.style.marginBottom = "0.3rem";
          item.style.borderRadius = "6px";
          item.style.background = "rgba(255, 255, 255, 0.02)";
          item.style.borderLeft = `3px solid ${isStaged ? 'var(--accent-success)' : 'var(--accent-warning)'}`;
          item.textContent = file;
          gitStatusList.appendChild(item);
        });
      } else {
        gitStatusList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">Workspace is clean. No uncommitted modifications.</p>';
      }
    }

    // 6. Collaborative Module Locks
    const locksList = document.getElementById('locks-list');
    if (locksList) {
      locksList.innerHTML = '';
      if (data.locks && data.locks.length > 0) {
        data.locks.forEach(lock => {
          const item = document.createElement('div');
          item.className = 'lock-card';
          item.innerHTML = `
            <span class="lock-title">${lock.module}</span>
            <div class="lock-meta">Locked: ${lock.timestamp}</div>
            <span class="lock-branch-badge">${lock.branch}</span>
          `;
          locksList.appendChild(item);
        });
      } else {
        locksList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No active module locks found. Run <code>./helper.sh lock &lt;module&gt;</code> to lock.</p>';
      }
    }

    // 7. Lessons Learned
    const lessonsList = document.getElementById('lessons-list');
    if (lessonsList) {
      lessonsList.innerHTML = '';
      if (data.lessons && data.lessons.length > 0) {
        data.lessons.forEach(lesson => {
          const item = document.createElement('div');
          item.className = 'rule-item';
          item.style.padding = "0.6rem 0.8rem";
          item.style.background = "rgba(255, 255, 255, 0.02)";
          item.style.borderRadius = "8px";
          item.style.borderLeft = "3px solid var(--accent-warning)";
          item.style.marginBottom = "0.5rem";
          item.style.fontSize = "0.85rem";
          item.textContent = lesson;
          lessonsList.appendChild(item);
        });
      } else {
        lessonsList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No lessons learned recorded yet.</p>';
      }
    }

    // 8. Synthesized Rules
    const rulesList = document.getElementById('rules-list');
    if (rulesList) {
      rulesList.innerHTML = '';
      if (data.rules && data.rules.length > 0) {
        data.rules.forEach(rule => {
          const item = document.createElement('div');
          item.className = 'rule-item';
          item.style.padding = "0.6rem 0.8rem";
          item.style.background = "rgba(255, 255, 255, 0.02)";
          item.style.borderRadius = "8px";
          item.style.borderLeft = "3px solid var(--accent-primary)";
          item.style.marginBottom = "0.5rem";
          item.style.fontSize = "0.85rem";
          item.textContent = rule;
          rulesList.appendChild(item);
        });
      } else {
        rulesList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No synthesized rules recorded yet.</p>';
      }
    }

    // 9. SemVer Releases
    const changelogList = document.getElementById('changelog-list');
    if (changelogList) {
      changelogList.innerHTML = '';
      if (data.changelog && data.changelog.length > 0) {
        data.changelog.forEach(release => {
          const item = document.createElement('div');
          item.className = 'changelog-row';
          item.innerHTML = `
            <span class="changelog-v">v${release.version}</span>
            <span class="text-muted" style="font-size: 0.8rem;">${release.date}</span>
          `;
          changelogList.appendChild(item);
        });
      } else {
        changelogList.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">No release history found.</p>';
      }
    }

  } catch (err) {
    console.error('Failed to load status:', err);
    refreshBtns.forEach(btn => {
      btn.disabled = false;
      btn.textContent = 'Refresh Audit';
    });
  }
};

// Auto run on load
document.addEventListener('DOMContentLoaded', () => {
  window.loadData(false);
  window.loadProfiles();
});

// Poll dashboard data every 5 seconds if document is visible
setInterval(() => {
  if (document.visibilityState === 'visible') {
    window.loadData(false);
    window.loadProfiles();
  }
}, 5000);

// Global function to copy public key to clipboard
window.copyPublicKey = function() {
  const box = document.getElementById('pubkey-content');
  if (!box) return;
  navigator.clipboard.writeText(box.textContent).then(() => {
    const btn = document.getElementById('copy-pubkey-btn');
    if (btn) {
      const origText = btn.textContent;
      btn.textContent = 'Copied!';
      btn.style.background = 'var(--accent-success)';
      setTimeout(() => {
        btn.textContent = origText;
        btn.style.background = '';
      }, 2000);
    }
  });
};

// Global function to switch git profiles
window.handleSwitchProfile = async function(name) {
  try {
    const res = await fetch('/api/profiles/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name })
    });
    const result = await res.json();
    if (result.success) {
      window.loadProfiles();
      window.loadData(true); // Force run validation status on profile switch
    } else {
      alert('Error switching profile: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to switch profile:', err);
  }
};

// Global function to handle new profile creation
window.handleCreateProfile = async function(event) {
  event.preventDefault();
  const name = document.getElementById('prof-name').value.trim();
  const email = document.getElementById('prof-email').value.trim();
  const signingKey = document.getElementById('prof-gpg').value.trim() || null;
  const sshKeyPath = document.getElementById('prof-ssh-path').value.trim() || null;
  const gitToken = document.getElementById('prof-token').value.trim() || null;
  const generateSsh = document.getElementById('prof-gen-ssh').checked;
  const switchAfter = document.getElementById('prof-switch-after').checked;

  const btn = event.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Registering...';

  try {
    const res = await fetch('/api/profiles/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        email: email,
        signing_key: signingKey,
        ssh_key_path: sshKeyPath,
        git_token: gitToken,
        generate_ssh: generateSsh,
        switch_after: switchAfter
      })
    });
    const result = await res.json();
    if (result.success) {
      document.getElementById('create-profile-form').reset();
      window.loadProfiles();
      window.loadData(true);
      alert('Profile registered successfully!');
    } else {
      alert('Error registering profile: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('Failed to create profile:', err);
    alert('Failed to connect to the server.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Profile';
  }
};

// Load Git profiles list and active details
window.loadProfiles = async function() {
  try {
    const res = await fetch('/api/profiles');
    if (!res.ok) return;
    const data = await res.json();
    const profiles = data.profiles || [];
    
    // Find active profile
    const active = profiles.find(p => p.active);
    
    // 1. Render Active Profile Details Card
    const detailsContainer = document.getElementById('active-profile-details');
    if (detailsContainer) {
      if (active) {
        let keyRowHtml = '';
        if (active.ssh_key_path) {
          keyRowHtml = `
            <div class="label">SSH Key Path:</div>
            <div class="val">${active.ssh_key_path}</div>
          `;
        } else if (active.signing_key) {
          keyRowHtml = `
            <div class="label">Signing Key:</div>
            <div class="val">${active.signing_key}</div>
          `;
        }
        
        detailsContainer.innerHTML = `
          <div class="profile-details-table">
            <div class="label">Name:</div>
            <div class="val">${active.name}</div>
            <div class="label">Email:</div>
            <div class="val">${active.email}</div>
            ${keyRowHtml}
            <div class="label">GitHub PAT:</div>
            <div class="val">${active.git_token ? '•••••••••••• (Configured)' : 'None'}</div>
          </div>
          <div id="ssh-pubkey-display" style="display:none;"></div>
        `;
        
        // If profile has SSH key path, fetch and display public key
        if (active.ssh_key_path) {
          try {
            const pubRes = await fetch(`/api/ssh/public-key?profile=${encodeURIComponent(active.name)}`);
            if (pubRes.ok) {
              const pubData = await pubRes.json();
              if (pubData.public_key) {
                const pubDisplay = document.getElementById('ssh-pubkey-display');
                if (pubDisplay) {
                  pubDisplay.style.display = 'block';
                  pubDisplay.innerHTML = `
                    <div class="pubkey-container">
                      <div class="pubkey-header">
                        <h3>🔑 Ed25519 Public Key</h3>
                        <button class="btn-secondary" id="copy-pubkey-btn" onclick="window.copyPublicKey()">Copy Key</button>
                      </div>
                      <div class="pubkey-box" id="pubkey-content">${pubData.public_key}</div>
                    </div>
                  `;
                }
              }
            }
          } catch (pubErr) {
            console.error('Failed to load public key:', pubErr);
          }
        }
      } else {
        detailsContainer.innerHTML = `
          <p class="text-muted" style="font-size:0.85rem; margin:0;">
            No active Git profile set up. Use the form to register one.
          </p>
        `;
      }
    }
    
    // 2. Render Registered Profiles List
    const listContainer = document.getElementById('profiles-list-container');
    if (listContainer) {
      listContainer.innerHTML = '';
      if (profiles.length > 0) {
        profiles.forEach(p => {
          const isCurrent = p.active;
          const card = document.createElement('div');
          card.className = 'profile-card' + (isCurrent ? ' active' : '');
          
          let actionHtml = '';
          if (isCurrent) {
            actionHtml = `<span class="status-badge pass" style="font-size:0.7rem; font-weight:600;">ACTIVE</span>`;
          } else {
            actionHtml = `<button class="btn-secondary" onclick="window.handleSwitchProfile('${p.name}')">Switch</button>`;
          }
          
          card.innerHTML = `
            <div class="profile-info">
              <span class="name">${p.name}</span>
              <span class="email">${p.email}</span>
            </div>
            <div class="profile-action">
              ${actionHtml}
            </div>
          `;
          listContainer.appendChild(card);
        });
      } else {
        listContainer.innerHTML = '<p class="text-muted" style="font-size: 0.85rem; margin:0;">No registered profiles found.</p>';
      }
    }
    
  } catch (err) {
    console.error('Failed to load profiles:', err);
  }
};
