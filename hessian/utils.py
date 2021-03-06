import torch
from matplotlib import pyplot as plt

def calculateDominance(H, tau = 0.00001):
    if H.numel() != 15080 ** 2:
        raise NotImplementedError
    diag = torch.diag(H.new(H.shape[0]).fill_(1))
    reg = H + diag * tau
    coords = generate_kernel_coords()

    sum_diag = torch.diag(reg).abs().sum().item()
    sum_all  = reg.abs().sum().item()
    sum_block=0
    for (a,b) in coords:
        sum_block += reg[a:b,a:b].abs().sum().item()

    print(f"Sum of diagonal         : {sum_diag:.2f}")
    print(f"Sum of kernel diagonal  : {sum_block:.2f}")
    print(f"Sum of all elements     : {sum_all:.2f}")
    print(f"Diagonal Dominance      : {sum_diag/sum_all:.8f} (1/{int(sum_all/sum_diag)})")
    print(f"Kernel Dominance        : {sum_block/sum_all:.8f} (1/{int(sum_all/sum_block)})")

    return sum_diag/sum_all, sum_block/sum_all

def calculateEigval(H, regParam = 0.00001):
    if H.numel() != 15080 ** 2:
        raise NotImplementedError
    diag = torch.diag(H.new(H.shape[0]).fill_(1))
    reg = H + diag * regParam
    # coords = generate_kernel_coords()

    try:
        eig = torch.eig(reg[:1000,:1000])[0].cpu()
    except:
        eig = torch.linalg.eigvals(reg[:1000,:1000])[0].cpu()

    if eig[:,1].abs().max() > 1e-30:
        raise ValueError('The eigenvalues of the matrix contain imaginary parts')
    
    eig = eig[:,0]
    plt.scatter(eig,torch.zeros_like(eig))
    return eig.mean(),eig.std()

    # H_kernel = torch.zeros_like(reg)
    # for (a,b) in coords:
    #     H_kernel[a:b,a:b] = reg[a:b,a:b]
    # try:
    #     eig_k = torch.eig(H_kernel[:3000,:3000])
    # except:
    #     eig_k = torch.linalg.eigvals(H_kernel)

    # H_kernel = torch.zeros_like(reg)
    # for (a,b) in coords:
    #     H_kernel[a:b,a:b] = reg[a:b,a:b]

def generate_kernel_diag(H, tau = 0):
    if H.numel() != 15080 ** 2:
        raise NotImplementedError
    res = torch.zeros_like(H)
    diag = torch.diag(H.new(H.shape[0]).fill_(1))
    H += diag * tau
    for (a,b) in generate_kernel_coords():
        res[a:b,a:b] = H[a:b,a:b]

    return res

def generate_kernel_coords():
    # 15080
    coords = []
    curr = 0

    for _ in range(5):
        coords.append((curr,curr+5*5))
        curr += 5*5
    coords.append((curr,curr+5))
    curr += 5

    for _ in range(10):
        coords.append((curr,curr+5*5*5))
        curr += 5*5*5
    coords.append((curr,curr+10))
    curr += 10

    for _ in range(80):
        coords.append((curr,curr+10*4*4))
        curr += 10*4*4
    coords.append((curr,curr+80))
    curr += 80

    for _ in range(10):
        coords.append((curr,curr+80))
        curr += 80
    coords.append((curr,curr+10))

    return coords

def get_near_psd(A, epsilon):
    C = (A + A.T)/2
    eigval, eigvec = torch.linalg.eig(C.to(torch.double))
    eigval[eigval.real < epsilon] = epsilon
    return eigvec @ (torch.diag(eigval)) @ eigvec.t()


def gradient(y, x, grad_outputs=None):
    """Compute dy/dx @ grad_outputs"""
    if grad_outputs is None:
        grad_outputs = torch.ones_like(y)
    grad = torch.autograd.grad(y, [x], grad_outputs = grad_outputs, create_graph=True, retain_graph=True, allow_unused=True)[0]
    return grad

def jacobian(y, x, device):
    '''
    Compute dy/dx = dy/dx @ grad_outputs; 
    y: output, batch_size * class_number
    x: parameter
    '''
    jac = torch.zeros(y.shape[1], torch.flatten(x).shape[0]).to(device)
    for i in range(y.shape[1]):
        grad_outputs = torch.zeros_like(y)
        grad_outputs[:,i] = 1
        jac[i,:] = torch.flatten(gradient(y, x, grad_outputs))
    return jac

def plot_tensors(tensor):
    if not tensor.ndim == 2:
        raise Exception("assumes a 2D tensor")
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1,1,1)
    ax.imshow(tensor.cpu().numpy())
    ax.axis('off')
    ax.set_xticklabels([])
    ax.set_yticklabels([])   
